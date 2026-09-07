"""Real dependency integration tests. Explicit skips are outstanding checks."""
import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from navigator.common import ROOT, digest, load_config, read_documents
from navigator.corpus import prepare


@unittest.skipUnless(importlib.util.find_spec("minsearch"), "minsearch installation not authorized/available yet")
class SearchRuntimeTests(unittest.TestCase):
    def test_real_index_preserves_filters_and_identity(self):
        from navigator.retrieval import Retriever
        docs, _, _ = prepare()
        engine = Retriever(docs, load_config())
        hits = engine.search("retrospective study", {"source_id": "PMC8039127"})
        self.assertTrue(hits)
        self.assertTrue(all(h["source_id"] == "PMC8039127" for h in hits))
        self.assertTrue(all(h["id"] in {d["id"] for d in docs} for h in hits))


@unittest.skipUnless(importlib.util.find_spec("dlt") and importlib.util.find_spec("duckdb"), "dlt/DuckDB installation not authorized/available yet")
class IngestionRuntimeTests(unittest.TestCase):
    def test_real_load_export_and_second_run(self):
        from navigator.corpus import ingest
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {"NAVIGATOR_RUNTIME": temp}):
            first = ingest(); one = read_documents()
            second = ingest(); two = read_documents()
            self.assertEqual(first["corpus_id"], second["corpus_id"])
            self.assertEqual(digest(one), digest(two))


@unittest.skipUnless(all(importlib.util.find_spec(m) for m in ["streamlit", "minsearch", "dlt", "duckdb"]), "UI integration dependencies not available")
class UIRuntimeTests(unittest.TestCase):
    def test_missing_corpus_shows_setup_error(self):
        from streamlit.testing.v1 import AppTest
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {"NAVIGATOR_RUNTIME": temp, "ENABLE_PAID_LLM": "0"}):
            app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
            self.assertFalse(app.exception)
            self.assertIn("Setup is incomplete", app.error[0].value)

    def test_real_streamlit_question_and_feedback(self):
        from streamlit.testing.v1 import AppTest
        from navigator.corpus import ingest
        from navigator.storage import Journal
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {"NAVIGATOR_RUNTIME": temp, "TELEMETRY_BACKEND": "jsonl", "ENABLE_PAID_LLM": "0"}):
            ingest()
            app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
            self.assertFalse(app.exception)
            app.text_area[0].set_value("What limitations does the retrospective Italian study describe?")
            app.button[0].click().run()
            self.assertFalse(app.exception)
            self.assertEqual(len(Journal(Path(temp)/"events.jsonl").read()[0]), 1)
            feedback_button = next(b for b in app.button if b.label == "Save feedback")
            feedback_button.click().run()
            self.assertFalse(app.exception)
            self.assertEqual(len(Journal(Path(temp)/"events.jsonl").read()[1]), 1)
            # A separate browser session must not inherit the first session's answer.
            other = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
            self.assertFalse(other.exception)
            self.assertFalse(any(b.label == "Save feedback" for b in other.button))
            # Rerunning widgets must not silently create another answer or vote.
            feedback_button.click().run()
            answers, feedback = Journal(Path(temp)/"events.jsonl").read()
            self.assertEqual(len(answers), 1)
            self.assertEqual(len(feedback), 1)
