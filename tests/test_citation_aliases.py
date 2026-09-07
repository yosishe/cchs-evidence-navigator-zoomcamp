"""Citation transport fixtures; no model-quality or scientific evidence."""
import copy
import json
import unittest

from navigator.common import digest
from navigator.rag import generate, run_request
from navigator.exports import comparison_rows
from navigator.experiments import verify_candidate_record
from config_fixtures import mock_config
import test_core_completion as fixtures
import test_local_quality as local_fixtures


class CitationAliasTests(unittest.TestCase):
    def config(self):
        return mock_config(prompt="short_ids", model_digest="fixture-digest")

    def payload(self, hit=None):
        hit = hit or fixtures.HIT
        return {"status": "answered", "claims": [{"text": hit["content"],
                "evidence_id": "E1", "exact_quote": hit["content"]}],
                "limitations": "Synthetic transport fixture."}

    def test_alias_decodes_to_canonical_identity_without_changing_quote_or_export(self):
        payload = self.payload()
        rec = generate("question", [fixtures.HIT], self.config(), "fixture-corpus",
                       use_llm=True, client=local_fixtures.local_client(payload))
        self.assertEqual(rec["status"], "answered")
        self.assertEqual(json.loads(rec["raw_output"])["claims"][0]["evidence_id"], "E1")
        self.assertEqual(rec["claims"][0]["evidence_id"], fixtures.HIT["id"])
        self.assertEqual(rec["claims"][0]["exact_quote"], payload["claims"][0]["exact_quote"])
        rows = comparison_rows(rec)
        self.assertEqual(rows[0]["evidence_id"], fixtures.HIT["id"])
        self.assertEqual(rows[0]["scientific_review"], "PENDING_HUMAN_REVIEW")

    def test_unknown_labels_quotes_and_extra_fields_remain_rejected(self):
        updates = [{"evidence_id": x} for x in ["E999", fixtures.HIT["id"], None, []]]
        updates += [{"exact_quote": "Text absent from the source"}, {"source_url": "injected"}]
        for update in updates:
            payload = self.payload(); payload["claims"][0].update(update)
            with self.subTest(update=update):
                rec = generate("question", [fixtures.HIT], self.config(), "fixture-corpus",
                               use_llm=True, client=local_fixtures.local_client(payload))
                self.assertEqual(rec["status"], "error")
                self.assertEqual(rec["error_stage"], "output_validation")
                self.assertEqual(rec["claims"], [])
                self.assertEqual(len(rec["calls"]), 1)

    def test_same_alias_is_scoped_to_each_request(self):
        for key, text in [("source-A:window-1", "First exact text."),
                          ("source-B:window-9", "Second exact text.")]:
            hit = {**fixtures.HIT, "id": key, "content": text}
            rec = generate("question", [hit], self.config(), digest([hit]),
                           use_llm=True, client=local_fixtures.local_client(self.payload(hit)))
            self.assertEqual(rec["citation_aliases"], {"E1": key})
            self.assertEqual(rec["claims"][0]["evidence_id"], key)

    def test_selection_reconstructs_raw_alias_mapping_and_rejects_tampering(self):
        cfg = self.config(); engine = fixtures.Engine()
        engine.corpus_id = digest([fixtures.HIT])
        question = {"question": "What was observed?"}
        rec = run_request(question["question"], engine, cfg,
                          client=local_fixtures.local_client(self.payload()), traffic_origin="evaluation")
        # Receipt-shaped synthetic fixture only, never written as real run evidence.
        rec["runtime_code_id"] = "fixture-code"
        rec["calls"][0].update(runtime_code_id="fixture-code", execution_kind="live_provider_client")
        row = {"record": rec, "prompt": "short_ids"}
        verify_candidate_record(row, question, cfg, [fixtures.HIT], "fixture-code")
        changed = copy.deepcopy(row)
        changed["record"]["citation_aliases"]["E1"] = "foreign-source"
        with self.assertRaises(ValueError):
            verify_candidate_record(changed, question, cfg, [fixtures.HIT], "fixture-code")
