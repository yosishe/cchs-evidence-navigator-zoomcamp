"""Public-release transport/evaluator challenges; synthetic fixtures, not quality data."""
import copy
import json
import unittest
from unittest.mock import patch, Mock

from navigator.common import digest, load_config
from navigator.rag import generate, run_request, decode_model_answer
from navigator.providers import model_identity, validate_provider, OWNER_MODEL_EXCEPTIONS
from navigator.experiments import verify_candidate_record
from navigator.evaluation import coverage_diagnostics, summarize_answer_review
from navigator.exports import comparison_rows
from config_fixtures import mock_config
import test_core_completion as fixtures
import test_local_quality as local


class NumberedCitationTests(unittest.TestCase):
    def setUp(self):
        self.hit = {**fixtures.HIT, "content": "The fictional study did not find 12 cases.\nIt found 10 cases.",
                    "start_in_passage": 80, "source_version": "synthetic-version"}
        self.cfg = mock_config(prompt="numbered_evidence", model_digest="fixture-digest")

    def payload(self, quote=None):
        return {"status": "answered", "claims": [{"text": "The fictional study found 10 cases.",
                "passage": 1, "quote": quote or self.hit["content"]}], "limitations": ""}

    def test_precision_prompt_keeps_numbered_transport_and_strict_schema(self):
        cfg = {**self.cfg, "prompt": "numbered_precise", "generation_json_schema": True}
        client = local.local_client(self.payload())
        rec = generate("Synthetic question", [self.hit], cfg, "fixture-corpus", use_llm=True, client=client)
        self.assertEqual(rec["status"], "answered")
        self.assertEqual(rec["claims"][0]["evidence_id"], self.hit["id"])
        properties = rec["calls"][0]["response_format"]["json_schema"]["schema"]["properties"]["claims"]["items"]["properties"]
        self.assertEqual(set(properties), {"text", "passage", "quote"})
        messages = rec["calls"][0]["messages"]
        self.assertNotIn("evidence_id", messages[-1]["content"])
        with self.assertRaises(ValueError):
            decode_model_answer(json.dumps(self.payload("It found 12 cases.")), [self.hit], cfg)

    def test_whitespace_resolution_keeps_raw_and_exact_source_offsets_and_exports(self):
        raw_quote = self.hit["content"].replace("\n", "  ")
        rec = generate("Synthetic question", [self.hit], self.cfg, "fixture-corpus", use_llm=True,
                       client=local.local_client(self.payload(raw_quote)))
        self.assertEqual(rec["status"], "answered")
        self.assertEqual(rec["claims"][0]["exact_quote"], self.hit["content"])
        receipt = rec["citation_resolutions"][0]
        self.assertEqual(receipt["raw_quote"], raw_quote)
        self.assertEqual(receipt["normalization"], "whitespace_only")
        self.assertEqual(receipt["start_in_passage"], 80)
        self.assertEqual(receipt["end_in_passage"], 80 + len(self.hit["content"]))
        self.assertEqual(comparison_rows(rec)[0]["exact_quote"], self.hit["content"])
        self.assertEqual(json.loads(rec["raw_output"])["claims"][0]["quote"], raw_quote)

    def test_negation_number_case_and_punctuation_changes_are_not_repaired(self):
        original = self.hit["content"]
        for bad in [original.replace("not ", ""), original.replace("10", "11"),
                    original.lower(), original.replace(".", "")]:
            with self.subTest(quote=bad), self.assertRaises(ValueError):
                decode_model_answer(json.dumps(self.payload(bad)), [self.hit], self.cfg)

    def test_ambiguous_quote_is_rejected_even_if_one_spelling_matches_exactly(self):
        hit = {**self.hit, "content": "A fact. A\nfact."}
        with self.assertRaises(ValueError):
            decode_model_answer(json.dumps(self.payload("A fact.")), [hit], self.cfg)

    def test_wrong_passage_and_invalid_number_types_are_rejected(self):
        other = {**self.hit, "id": "different-source", "content": "Another fictional observation."}
        for number in [0, -1, 3, True, 1.0, "1", None, [], 2]:
            bad = self.payload(); bad["claims"][0]["passage"] = number
            with self.subTest(number=number), self.assertRaises(ValueError):
                decode_model_answer(json.dumps(bad), [self.hit, other], self.cfg)

    def test_model_metadata_and_empty_quotes_still_fail(self):
        for update in [{"source_url": "injected"}, {"quote": " "}, {"evidence_id": self.hit["id"]}]:
            bad = self.payload(); bad["claims"][0].update(update)
            with self.subTest(update=update), self.assertRaises(ValueError):
                decode_model_answer(json.dumps(bad), [self.hit], self.cfg)

    def test_insufficient_evidence_is_canonical_and_has_no_citation_receipt(self):
        payload = {"status": "insufficient_evidence", "claims": [], "limitations": "Corpus gap."}
        receipts = []
        self.assertEqual(decode_model_answer(json.dumps(payload), [self.hit], self.cfg,
                         resolutions=receipts), payload)
        self.assertEqual(receipts, [])

    def test_candidate_replay_detects_changed_resolution_offsets(self):
        engine = fixtures.Engine(); engine.search = lambda *a, **kw: [self.hit]
        engine.corpus_id = digest([self.hit]); question = {"question": "Synthetic question"}
        rec = run_request(question["question"], engine, self.cfg,
            client=local.local_client(self.payload()), traffic_origin="evaluation")
        rec["runtime_code_id"] = "fixture-code"
        rec["calls"][0].update(runtime_code_id="fixture-code", execution_kind="live_provider_client")
        row = {"record": rec, "prompt": "numbered_evidence"}
        verify_candidate_record(row, question, self.cfg, [self.hit], "fixture-code")
        changed = copy.deepcopy(row)
        changed["record"]["citation_resolutions"][0]["start_in_chunk"] += 1
        with self.assertRaises(ValueError):
            verify_candidate_record(changed, question, self.cfg, [self.hit], "fixture-code")


class OwnerModelExceptionTests(unittest.TestCase):
    def test_only_named_model_and_approved_weights_are_allowed(self):
        cfg = {**load_config(), "model": "gemma3:12b"}
        self.assertEqual(validate_provider(cfg), "ollama")
        for update in [{"model": "gemma3:27b"}, {"model_digest": "different"}]:
            with self.subTest(update=update), self.assertRaises(ValueError):
                validate_provider({**cfg, **update})

    def test_installed_digest_is_checked_even_without_config_digest(self):
        cfg = {**load_config(), "model": "gemma3:12b"}
        for identity in [OWNER_MODEL_EXCEPTIONS[cfg["model"]], "unexpected-weights"]:
            response = Mock(); response.json.return_value = {
                "models": [{"name": cfg["model"], "digest": identity, "size": 1}]}
            with patch("requests.Session") as session:
                session.return_value.get.return_value = response
                if identity == "unexpected-weights":
                    with self.assertRaises(ValueError): model_identity(cfg)
                else:
                    self.assertEqual(model_identity(cfg)["digest"], identity)


class DiagnosticCoverageTests(unittest.TestCase):
    def test_empty_or_unknown_requirements_cannot_report_perfect_coverage(self):
        output = coverage_diagnostics([{"fact_coverage": [], "qualification_coverage": []}])
        self.assertEqual(output["fact_coverage"]["denominator"], 0)
        self.assertIsNone(output["fact_coverage"]["fully_covered_rate"])
        self.assertIsNone(coverage_diagnostics([], False)["fact_coverage"]["counts"])

    def test_partial_coverage_does_not_upgrade_acceptance(self):
        results, reviews = local.CompletenessTests().fixture()
        reviews["reviews"][0]["fact_coverage"][0] = "partial"
        summary = summarize_answer_review(results, reviews)
        self.assertFalse(summary["per_question"][0]["acceptable"])
        diagnostics = summary["aggregates"][0]["coverage_diagnostics"]
        self.assertEqual(diagnostics["fact_coverage"]["counts"]["partial"], 1)


if __name__ == "__main__":
    unittest.main()
