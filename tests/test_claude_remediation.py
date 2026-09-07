"""Setup and evaluation failure regressions; every model output here is synthetic."""
import copy
import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from navigator.common import ROOT, digest, load_config
from navigator.evaluation import answer_evaluation, summarize_answer_review
from navigator.experiments import select_generation
from navigator.preflight import inspect_runtime
from navigator.providers import complete
import test_core_completion as fixtures
from config_fixtures import mock_config


class ProviderSetupTests(unittest.TestCase):
    def test_length_limited_completion_is_retained_as_failed_output(self):
        from navigator.rag import generate
        sdk = fixtures.client()
        response = sdk.chat.completions.create()
        response.choices[0].finish_reason = "length"
        sdk.chat.completions.create = MagicMock(return_value=response)
        rec = generate("question", [fixtures.HIT], mock_config(), "fixture",
                       use_llm=True, client=sdk)
        self.assertEqual(rec["status"], "error")
        self.assertEqual(rec["error_stage"], "output_validation")
        self.assertEqual(rec["claims"], [])
        self.assertEqual(rec["calls"][0]["status"], "completed")
        self.assertEqual(rec["calls"][0]["finish_reason"], "length")
        self.assertEqual(json.loads(rec["raw_output"]), fixtures.PAYLOAD)
        self.assertEqual(rec["output_tokens"], 15)
        self.assertEqual(sdk.chat.completions.create.call_count, 1)

    def test_json_mode_is_sent_and_recorded_without_weakening_validation(self):
        for enabled in (True, False):
            with self.subTest(json_mode=enabled):
                sdk = fixtures.client()
                call = MagicMock(wraps=sdk.chat.completions.create)
                sdk.chat.completions.create = call
                cfg = mock_config(json_mode=enabled)
                ledger = []
                complete(cfg, [{"role": "user", "content": "Return JSON"}],
                         stage="generation", ledger=ledger, client=sdk)
                self.assertEqual(call.call_count, 1)
                self.assertEqual(call.call_args.kwargs.get("response_format"),
                                 {"type": "json_object"} if enabled else None)
                self.assertIs(ledger[0]["json_mode"], enabled)
                self.assertEqual(ledger[0]["execution_kind"], "sdk_fixture")
                self.assertEqual(ledger[0]["request_timeout_seconds"], cfg["request_timeout_seconds"])

    def test_timeout_override_is_validated_and_fingerprinted(self):
        with patch.dict(os.environ, {"NAVIGATOR_REQUEST_TIMEOUT": ""}):
            baseline = load_config()
        with patch.dict(os.environ, {"NAVIGATOR_REQUEST_TIMEOUT": str(baseline["request_timeout_seconds"])}):
            self.assertEqual(digest(load_config()), digest(baseline))
        with patch.dict(os.environ, {"NAVIGATOR_REQUEST_TIMEOUT": "240.5"}):
            self.assertEqual(load_config()["request_timeout_seconds"], 240.5)
            self.assertNotEqual(digest(load_config()), digest(baseline))
        for invalid in ("0", "-1", "nan", "inf", "abc"):
            with self.subTest(value=invalid), patch.dict(os.environ, {"NAVIGATOR_REQUEST_TIMEOUT": invalid}):
                with self.assertRaises(ValueError):
                    load_config()

    def test_generation_schema_sent_and_audited_but_not_used_for_rewrite(self):
        from navigator.providers import ANSWER_JSON_SCHEMA
        cfg = mock_config(generation_json_schema=True)
        for stage in ("generation", "rewrite"):
            sdk = fixtures.client()
            sdk.chat.completions.create = MagicMock(wraps=sdk.chat.completions.create)
            ledger = []
            complete(cfg, [{"role": "user", "content": "synthetic question"}],
                     stage=stage, ledger=ledger, client=sdk)
            actual = sdk.chat.completions.create.call_args.kwargs["response_format"]
            expected = ({"type": "json_schema", "json_schema": {
                "name": "evidence_answer", "strict": True, "schema": ANSWER_JSON_SCHEMA}}
                if stage == "generation" else {"type": "json_object"})
            self.assertEqual(actual, expected)
            self.assertEqual(ledger[0]["response_format"], expected)
            self.assertIs(ledger[0]["generation_json_schema"], stage == "generation")
            actual["type"] = "mutated fixture request"
            self.assertEqual(ledger[0]["response_format"], expected)

    def test_schema_mode_does_not_repair_invalid_citations_or_shape(self):
        from navigator.rag import generate
        changes = [lambda p: p["claims"][0].update(evidence_id="foreign-source"),
                   lambda p: p["claims"][0].update(exact_quote="invented quotation"),
                   lambda p: p.pop("limitations"),
                   lambda p: p.update(status="insufficient_evidence")]
        for change in changes:
            sdk = fixtures.client()
            response = sdk.chat.completions.create()
            payload = copy.deepcopy(fixtures.PAYLOAD)
            change(payload)
            response.choices[0].message.content = json.dumps(payload)
            sdk.chat.completions.create = MagicMock(return_value=response)
            rec = generate("question", [fixtures.HIT],
                           mock_config(generation_json_schema=True), "fixture",
                           use_llm=True, client=sdk)
            self.assertEqual(rec["status"], "error")
            self.assertEqual(rec["claims"], [])
            self.assertEqual(json.loads(rec["raw_output"]), payload)
            self.assertEqual(sdk.chat.completions.create.call_count, 1)

    def test_schema_mode_retains_length_failure_and_usage(self):
        from navigator.rag import generate
        sdk = fixtures.client()
        response = sdk.chat.completions.create()
        response.choices[0].finish_reason = "length"
        sdk.chat.completions.create = MagicMock(return_value=response)
        rec = generate("question", [fixtures.HIT],
                       mock_config(generation_json_schema=True), "fixture",
                       use_llm=True, client=sdk)
        self.assertEqual(rec["status"], "error")
        self.assertEqual(rec["output_tokens"], 15)
        self.assertEqual(rec["calls"][0]["finish_reason"], "length")
        self.assertTrue(rec["calls"][0]["generation_json_schema"])
        self.assertEqual(json.loads(rec["raw_output"]), fixtures.PAYLOAD)
        self.assertEqual(sdk.chat.completions.create.call_count, 1)

    def test_schema_provider_error_is_not_retried_or_downgraded(self):
        sdk = fixtures.client()
        sdk.chat.completions.create = MagicMock(side_effect=RuntimeError("schema unsupported"))
        ledger = []
        with self.assertRaises(RuntimeError):
            complete(mock_config(generation_json_schema=True), [],
                     stage="generation", ledger=ledger, client=sdk)
        self.assertEqual(sdk.chat.completions.create.call_count, 1)
        self.assertEqual(len(ledger), 1)
        self.assertEqual(ledger[0]["status"], "error")
        self.assertEqual(ledger[0]["response_format"]["type"], "json_schema")

    def test_schema_config_conflicts_rejected_before_any_call(self):
        for updates in ({"generation_json_schema": "true"},
                        {"generation_json_schema": 1},
                        {"generation_json_schema": True, "json_mode": False},
                        {"generation_json_schema": True, "provider": "openai"}):
            cfg = mock_config(**updates)
            with tempfile.TemporaryDirectory() as temp:
                path = Path(temp) / "config.json"
                path.write_text(json.dumps(cfg))
                with self.assertRaises(ValueError):
                    load_config(path)
            if cfg["provider"] == "ollama":
                sdk = fixtures.client()
                sdk.chat.completions.create = MagicMock(wraps=sdk.chat.completions.create)
                ledger = []
                with self.assertRaises(ValueError):
                    complete(cfg, [], stage="generation", ledger=ledger, client=sdk)
                self.assertEqual(ledger, [])
                sdk.chat.completions.create.assert_not_called()

    def fake_session(self, installed=True, running=True):
        session = MagicMock()
        session.__enter__.return_value = session
        metadata = {"api/version": {"version": "fictional-version"},
                    "api/tags": {"models": [{"name": "phi3:latest", "digest": "fixture", "size": 123}] if installed else []},
                    "api/ps": {"models": [{"digest": "fixture", "context_length": 2048}] if running else []}}
        session.get.side_effect = lambda url, **kwargs: SimpleNamespace(status_code=200,
            json=lambda: metadata[url.split("11434/")[1]])
        session.post.return_value = SimpleNamespace(status_code=200, json=lambda: {
            "model_info": {"phi3.context_length": 4096, "unwanted": "omit"},
            "details": {"quantization_level": "Q4-fixture"}})
        return session

    def test_metadata_distinguishes_architecture_and_loaded_context_without_inference(self):
        for running in (True, False):
            session = self.fake_session(running=running)
            with patch("navigator.preflight.requests.Session", return_value=session), \
                 patch("navigator.preflight.shutil.which", return_value=None), \
                 patch("navigator.preflight.read_documents", return_value=[fixtures.HIT]):
                report = inspect_runtime(mock_config())
            self.assertEqual(report["status"], "RUNTIME_METADATA_READY")
            self.assertEqual(report["architecture_context_limits"], {"phi3.context_length": 4096})
            self.assertEqual(report["loaded_context_tokens"], 2048 if running else None)
            self.assertEqual(report["provider_requests"], 0)
            self.assertEqual(session.post.call_args.args[0], "http://localhost:11434/api/show")
            self.assertFalse(session.trust_env)
            self.assertFalse(session.post.call_args.kwargs["allow_redirects"])

    def test_missing_model_exits_nonzero_without_pull_or_show(self):
        from navigator.__main__ import emit_report
        session = self.fake_session(installed=False)
        with patch("navigator.preflight.requests.Session", return_value=session), \
             patch("navigator.preflight.shutil.which", return_value=None), \
             patch("navigator.preflight.read_documents", return_value=[fixtures.HIT]):
            report = inspect_runtime(mock_config())
        self.assertEqual(report["status"], "BLOCKED_RUNTIME_PREFLIGHT")
        self.assertEqual(report["next_setup_command_after_approval"], "ollama pull phi3")
        session.post.assert_not_called()
        with patch("builtins.print"), self.assertRaises(SystemExit) as raised:
            emit_report(report)
        self.assertEqual(raised.exception.code, 1)

    def test_dashboard_defaults_to_session_origin_and_stays_labeled(self):
        from navigator.corpus import ingest
        from streamlit.testing.v1 import AppTest
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {
                "NAVIGATOR_RUNTIME": tmp, "TELEMETRY_BACKEND": "jsonl", "NAVIGATOR_TRAFFIC_ORIGIN": "qa"}):
            ingest()
            app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
            origin = next(item for item in app.selectbox if item.label == "Activity origin")
            self.assertEqual(origin.value, "qa")
            self.assertFalse(app.exception)
            self.assertTrue(any("separately from researcher feedback" in item.value for item in app.info))


class EvaluationFailureTests(unittest.TestCase):
    def test_reference_diagnostic_keeps_invalid_outputs_but_stops_on_provider_failure(self):
        from navigator.experiments import diagnose_with_reference_context
        docs = [copy.deepcopy(fixtures.HIT)]
        results = {"config": mock_config(), "corpus_id": digest(docs),
                   "run_directory": "diagnostic-fixture", "questions": [
                       {"id": "q", "question": "What was observed?", "answerable": True,
                        "reference_quotes": [{"id": fixtures.HIT["id"]}]}],
                   "per_question": [{"question_id": "q", "prompt": p,
                                     "record": {"id": p, "status": "error"}}
                                    for p in ["evidence_first", "schema_first"]]}
        for stage, expected_calls in [("output_validation", 2), ("provider", 1)]:
            failure = {"status": "error", "error_stage": stage,
                       "calls": [{"id": "synthetic-receipt"}]}
            with self.subTest(stage=stage), tempfile.TemporaryDirectory() as tmp, \
                 patch("navigator.experiments.ROOT", Path(tmp)), \
                 patch("navigator.experiments.read_documents", return_value=docs), \
                 patch("navigator.experiments.generate", return_value=failure) as generate:
                report = diagnose_with_reference_context(results)
                self.assertEqual(generate.call_count, expected_calls)
                self.assertEqual(report["actual_provider_requests"], expected_calls)
                self.assertEqual(len(report["rows"]), expected_calls)
                self.assertEqual(report["status"], "EXECUTED_AWAITING_COMPARISON"
                                 if stage == "output_validation" else "STOPPED_ON_ERROR")

    def evaluate(self, failure):
        docs = [copy.deepcopy(fixtures.HIT)]
        questions = [{"id": "q", "question": "What was observed?", "answerable": True,
                      "split": "tuning", "slice": "direct", "required_facts": [{"text": "Ten adults"}],
                      "required_qualifications": [], "reference_quotes": []}]
        engine = fixtures.Engine()
        engine.corpus_id = digest(docs)
        sdk = fixtures.client()
        original = sdk.chat.completions.create
        attempts = []
        def call(**kwargs):
            attempts.append(kwargs)
            if len(attempts) == 1:
                if isinstance(failure, Exception):
                    raise failure
                return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=failure),
                                                                finish_reason="stop")], usage=None)
            return original(**kwargs)
        sdk.chat.completions.create = call
        with tempfile.TemporaryDirectory() as tmp, patch("navigator.evaluation.ROOT", Path(tmp)), \
             patch("navigator.evaluation.read_documents", return_value=docs), \
             patch("navigator.evaluation.load_question_bank", return_value={"questions": questions}), \
             patch("navigator.evaluation.Retriever", return_value=engine):
            result = answer_evaluation(config=mock_config(), client=sdk)
        return result, attempts

    def test_invalid_completed_output_is_counted_and_other_prompt_still_runs(self):
        result, calls = self.evaluate("not JSON")
        self.assertEqual(result["status"], "EXECUTED_AWAITING_REVIEW")
        self.assertEqual(len(calls), 2)
        self.assertEqual(result["actual_provider_requests"], 2)
        bad, good = result["per_question"]
        self.assertEqual(bad["record"]["error_stage"], "output_validation")
        self.assertEqual(bad["record"]["claims"], [])
        self.assertEqual(good["record"]["status"], "answered")
        reviews = {"reviewer": "fixture", "reviewer_kind": "assistant", "results_hash": digest(result), "reviews": []}
        for row in result["per_question"]:
            ok = row["record"]["status"] == "answered"
            reviews["reviews"].append({"answer_id": row["record"]["id"], "record_hash": row["record_hash"],
                "relevance": "relevant" if ok else "not_relevant", "claim_support": ["supported"] if ok else [],
                "fact_coverage": ["covered" if ok else "missing"], "qualification_coverage": [],
                "abstention_correct": False, "reason": "Synthetic output; malformed answer is a failure."})
        summary = summarize_answer_review(result, reviews)
        self.assertEqual(summary["status"], "REVIEWED_COMPLETE")
        self.assertEqual([a["acceptable_rate"] for a in summary["aggregates"]], [0, 1])
        self.assertEqual([a["errors"] for a in summary["aggregates"]], [1, 0])

    def test_provider_outage_still_stops_without_retries(self):
        result, calls = self.evaluate(ConnectionError("fictional service outage"))
        self.assertEqual(result["status"], "STOPPED_ON_ERROR")
        self.assertEqual(len(calls), 1)
        self.assertEqual(result["per_question"][0]["record"]["error_stage"], "provider")

    def test_selector_keeps_failed_alternative_but_rejects_fabricated_failure(self):
        for raw in ("not JSON", json.dumps(fixtures.PAYLOAD)):
            with self.subTest(raw=raw), tempfile.TemporaryDirectory() as tmp:
                folder = Path(tmp)
                rp, vp, docs, bank, result = fixtures.SelectionEvidenceTests().make_evidence(folder)
                review = json.loads(vp.read_text())
                bad = result["per_question"][0]
                bad["record"].update(status="error", error_stage="output_validation", claims=[], raw_output=raw)
                bad["record"]["calls"][0]["raw_output"] = raw
                bad["record_hash"] = digest(bad["record"])
                review["reviews"][0].update(record_hash=bad["record_hash"], relevance="not_relevant",
                                          claim_support=[], fact_coverage=["missing"])
                review["results_hash"] = digest(result)
                rp.write_text(json.dumps(result)); vp.write_text(json.dumps(review))
                fixtures.write_whole_fixture(folder, result, [False, True])
                with patch("navigator.experiments.ROOT", folder), \
                     patch("navigator.experiments.runtime_code_id", return_value="fixture-code"), \
                     patch("navigator.experiments.read_documents", return_value=docs), \
                     patch("navigator.experiments.load_question_bank", return_value=bank):
                    if raw == "not JSON":
                        selected = select_generation([rp], [vp])
                        self.assertEqual(selected["winner"]["prompt"], "evidence_first")
                        self.assertEqual(selected["candidates"][0]["errors"], 1)
                    else:
                        with self.assertRaises(ValueError):
                            select_generation([rp], [vp])


if __name__ == "__main__":
    unittest.main()
