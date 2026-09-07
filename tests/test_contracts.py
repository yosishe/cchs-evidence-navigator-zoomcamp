import copy
import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from navigator.common import csv_safe, digest, load_config
from navigator.corpus import normalize_source, prepare, verify_quote, windows
from navigator.evaluation import metrics, validate_questions
from navigator.rag import generate, validate_answer
from navigator.retrieval import embedding_text, reciprocal_rank_fusion
from navigator.storage import Journal
from config_fixtures import mock_config


def fixture():
    raw = json.dumps([{"documents": [{"id": "PMCTEST", "passages": [
        {"text": "TEST PHOX2B evidence with exact identifiers.", "offset": 100,
         "infons": {"section_type": "RESULTS", "type": "paragraph"}},
        {"text": "Reference only", "offset": 200,
         "infons": {"section_type": "REF", "type": "ref"}},
    ]}]}]).encode()
    src = {"source_id": "PMCTEST", "sha256": digest(raw), "title": "Synthetic fixture",
           "article_url": "https://example.org/fixture", "license": "synthetic"}
    return src, raw


class CorpusContractTests(unittest.TestCase):
    def test_csv_formula_neutralized_without_changing_plain_text(self):
        self.assertEqual(csv_safe('=HYPERLINK("bad")'), "'=HYPERLINK(\"bad\")")
        self.assertEqual(csv_safe("PHOX2B"), "PHOX2B")
    def test_windows_keep_exact_offsets_and_tail(self):
        # Keep the submitted source in English while exercising Unicode offsets.
        text = ("Gene " + chr(0x1F9EC) + " PHOX2B ") * 20
        chunks = list(windows(text, 30, 7))
        self.assertEqual(chunks[-1][1], len(text))
        for start, end, content in chunks:
            self.assertEqual(text[start:end], content)

    def test_invalid_overlap(self):
        with self.assertRaises(ValueError): list(windows("x", 2, 2))

    def test_hash_change_fails_closed(self):
        src, raw = fixture()
        with self.assertRaises(ValueError): normalize_source(src, raw+b" ", load_config())

    def test_identity_mismatch(self):
        src, raw = fixture(); src["source_id"] = "OTHER"
        with self.assertRaises(ValueError): normalize_source(src, raw, load_config())

    def test_bibliography_excluded_and_unknown_context_preserved(self):
        src, raw = fixture(); rows, excluded = normalize_source(src, raw, load_config())
        self.assertEqual(len(rows), 1); self.assertEqual(len(excluded), 1)
        self.assertEqual(rows[0]["population_or_model"], "unknown")
        self.assertIn("PHOX2B", rows[0]["content"])

    def test_repeat_preparation_same_ids_and_content(self):
        a, _, _ = prepare(); b, _, _ = prepare()
        self.assertEqual(digest(a), digest(b))
        self.assertEqual(len(a), len({r["id"] for r in a}))

    def test_real_corpus_quotes_have_no_invented_text(self):
        docs, _, _ = prepare()
        self.assertTrue(all(verify_quote(d, d["content"]) for d in docs))


class RetrievalEvaluationTests(unittest.TestCase):
    def test_embedding_template_keeps_selected_text_exact(self):
        doc = {"title": "Long title", "content": "Exact PHOX2B passage"}
        self.assertEqual(embedding_text(doc, "content"), doc["content"])
        self.assertEqual(embedding_text(doc, "title_content"), "Long title\nExact PHOX2B passage")
        with self.assertRaises(ValueError): embedding_text(doc, "invented")
    def test_mrr_one_based(self):
        self.assertEqual(metrics(["a", "b", "c"], ["b"]), {"hit":1, "reciprocal_rank":0.5})
        self.assertEqual(metrics([], ["b"])["hit"], 0)

    def test_rrf_zero_based_and_duplicate_safe(self):
        result = reciprocal_rank_fusion([[{"id":"a"}, {"id":"a"}, {"id":"b"}], [{"id":"b"}]], 50)
        self.assertEqual(result[0]["id"], "b")
        self.assertAlmostEqual(result[1]["score"], 1/50)

    def test_rrf_rejects_zero_constant(self):
        with self.assertRaises(ValueError): reciprocal_rank_fusion([], 0)

    def test_gold_missing_passage_is_invalid(self):
        q = [{"group_id":"x", "split":"test", "answerable":True, "relevant_ids":["missing"]}]
        with self.assertRaises(ValueError): validate_questions(q, [])

    def test_group_leakage_is_invalid(self):
        q = [{"group_id":"x", "split":s, "answerable":False, "relevant_ids":[]} for s in ["tuning","test"]]
        with self.assertRaises(ValueError): validate_questions(q, [])


class AnswerTests(unittest.TestCase):
    def setUp(self):
        src, raw = fixture(); self.hits, _ = normalize_source(src, raw, load_config())
        self.cfg = mock_config(provider="openai", model="gpt-5.4-mini", json_mode=False)
        self.valid = {"status":"answered", "claims":[{"text":"A synthetic claim", "evidence_id":self.hits[0]["id"], "exact_quote":"PHOX2B"}], "limitations":"Synthetic unit test; not biomedical evidence."}

    def test_unknown_citation_rejected(self):
        bad = copy.deepcopy(self.valid); bad["claims"][0]["evidence_id"] = "invented"
        with self.assertRaises(ValueError): validate_answer(bad, self.hits)

    def test_altered_quote_rejected(self):
        bad = copy.deepcopy(self.valid); bad["claims"][0]["exact_quote"] = "PHOX2A"
        with self.assertRaises(ValueError): validate_answer(bad, self.hits)

    def test_empty_supported_answer_rejected(self):
        bad = copy.deepcopy(self.valid); bad["claims"] = []
        with self.assertRaises(ValueError): validate_answer(bad, self.hits)

    def test_preview_has_no_generated_claims_or_token_usage(self):
        rec = generate("test", self.hits, self.cfg, "fixture")
        self.assertEqual(rec["status"], "preview"); self.assertEqual(rec["claims"], [])
        self.assertIsNone(rec["input_tokens"]); self.assertIsNone(rec["cost_usd"])

    def test_empty_search_does_not_call_provider(self):
        client = SimpleNamespace(responses=None)
        rec = generate("test", [], self.cfg, "fixture", paid=True, client=client)
        self.assertEqual(rec["status"], "insufficient_evidence")

    def test_paid_calls_disabled_by_default(self):
        with patch.dict(os.environ, {"ENABLE_PAID_LLM":"0"}):
            rec = generate("test", self.hits, self.cfg, "fixture", paid=True)
        self.assertEqual(rec["status"], "error")

    def test_mock_sdk_contract_and_actual_usage(self):
        response = SimpleNamespace(output_text=json.dumps(self.valid), usage=SimpleNamespace(input_tokens=17, output_tokens=9))
        calls = []
        client = SimpleNamespace(responses=SimpleNamespace(create=lambda **kw: (calls.append(kw) or response)))
        with patch.dict(os.environ, {"ENABLE_PAID_LLM":"1"}):
            rec = generate("test", self.hits, self.cfg, "fixture", paid=True, client=client)
        self.assertEqual(rec["status"], "answered"); self.assertEqual(rec["input_tokens"], 17)
        self.assertEqual(calls[0]["input"][0]["role"], "developer")

    def test_malformed_provider_output_never_becomes_answer(self):
        client = SimpleNamespace(responses=SimpleNamespace(create=lambda **kw: SimpleNamespace(output_text="bad json",usage=None)))
        with patch.dict(os.environ, {"ENABLE_PAID_LLM":"1"}):
            rec = generate("test", self.hits, self.cfg, "fixture", paid=True, client=client)
        self.assertEqual(rec["status"], "error"); self.assertFalse(rec["claims"])

    def test_provider_timeout_is_bounded_and_does_not_expose_secret(self):
        calls = []
        def fail(**kwargs):
            calls.append(kwargs)
            raise TimeoutError("synthetic-secret-must-not-be-displayed")
        client = SimpleNamespace(responses=SimpleNamespace(create=fail))
        with patch.dict(os.environ, {"ENABLE_PAID_LLM":"1"}):
            rec = generate("test", self.hits, self.cfg, "fixture", paid=True, client=client)
        self.assertEqual(len(calls), 1)
        self.assertEqual(rec["status"], "error")
        self.assertFalse(rec["claims"])
        self.assertNotIn("synthetic-secret", json.dumps(rec))


class FeedbackTests(unittest.TestCase):
    def test_feedback_persists_and_duplicate_submission_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/"journal.jsonl"; store = Journal(path)
            store.save_answer({"id":"a", "traffic_origin":"user"}); store.save_answer({"id":"a", "traffic_origin":"user"})
            store.save_feedback("a",1,feedback_id="f"); store.save_feedback("a",1,feedback_id="f")
            answers, feedback = Journal(path).read()
            self.assertEqual(len(answers),1); self.assertEqual(len(feedback),1)
            self.assertEqual(feedback[0]["answer_id"],"a")

    def test_dangling_feedback_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError): Journal(Path(temp)/"journal").save_feedback("missing",1)

    def test_invalid_feedback_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError): Journal(Path(temp)/"journal").save_feedback("a",True)


if __name__ == "__main__":
    unittest.main()
