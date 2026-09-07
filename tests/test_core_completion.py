"""Core grading evidence contracts; synthetic SDK fixtures are not model quality."""
import copy
import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from navigator.common import digest, load_config
from navigator.corpus import prepare
from navigator.rag import prepare_context, run_request
from navigator.evaluation import answer_plan, answer_evaluation
from navigator.__main__ import emit_report, main
from config_fixtures import mock_config

HIT = {"id": "fixture:1", "title": "Fictional source", "section": "RESULTS",
       "article_type": "fictional", "content": "Ten adults were observed.",
       "rank": 1, "source_id": "fixture"}
PAYLOAD = {"status": "answered", "claims": [{"text": "Ten adults were observed.",
           "evidence_id": "fixture:1", "exact_quote": "Ten adults were observed."}],
           "limitations": "Synthetic software fixture."}


def write_whole_fixture(folder, results, acceptable=None):
    """Synthetic sidecar for selection contracts; never a real source judgment."""
    from navigator.whole_review import whole_review_template
    whole = whole_review_template(results)
    whole.update(reviewer="synthetic-validator-fixture", reviewer_kind="assistant")
    for i, row in enumerate(whole["reviews"]):
        row.update(visible_prose_supported=True, export_preserves_qualifications=True,
                   acceptable=True if acceptable is None else acceptable[i],
                   reason="Synthetic contract fixture, not scientific support.")
    (folder / "whole-answer-review.json").write_text(json.dumps(whole))
    return whole


class Engine:
    corpus_id = "fixture-corpus"

    def search(self, query, filters=None, trace=None):
        self.last = (query, filters)
        if trace is not None:
            trace["query"] = query
        return [copy.deepcopy(HIT)]


def client():
    def complete(**kwargs):
        return SimpleNamespace(choices=[SimpleNamespace(
            message=SimpleNamespace(content=json.dumps(PAYLOAD)), finish_reason="stop")],
            usage=SimpleNamespace(prompt_tokens=20, completion_tokens=15))
    return SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=complete)))


class SharedFlowTests(unittest.TestCase):
    def test_compact_metadata_keeps_scientific_context_and_export_provenance(self):
        from navigator.experiments import verify_candidate_record
        from navigator.exports import comparison_rows
        hit = {**HIT, "source_version": "fixture-version", "source_url": "https://example.invalid/source",
               "year": "2020", "section_heading": "Observations",
               "population_or_model": "Adults in a fictional observation"}
        engine = Engine()
        engine.search = lambda *args, **kwargs: [copy.deepcopy(hit)]
        engine.corpus_id = digest([hit])
        cfg = mock_config(model_digest="fixture-digest")
        question = {"question": "What was observed?"}
        prepared = prepare_context(question["question"], engine, cfg)
        rec = run_request(question["question"], engine, {**cfg, "prompt": "compact_metadata"},
                          prepared_context=prepared, client=client())
        sent = json.loads(rec["calls"][0]["messages"][1]["content"])["passages"][0]
        canonical = json.loads(rec["context"])[0]
        self.assertEqual(rec["context_id"], prepared["context_id"])
        for key in ["evidence_id", "text", "title", "section", "section_heading", "article_type",
                    "year", "population_or_model"]:
            self.assertEqual(sent[key], canonical[key])
        for key in ["source_version", "source_url"]:
            self.assertNotIn(key, sent)
            self.assertEqual(canonical[key], hit[key])
            self.assertEqual(comparison_rows(rec)[0][key], hit[key])
        # Receipt-shaped fixtures exercise consistency, never live quality evidence.
        rec["runtime_code_id"] = "fixture-code"
        rec["calls"][0].update(runtime_code_id="fixture-code", execution_kind="live_provider_client")
        row = {"record": rec, "prompt": "compact_metadata"}
        verify_candidate_record(row, question, cfg, [hit], "fixture-code")
        changed = copy.deepcopy(row)
        messages = changed["record"]["calls"][0]["messages"]
        payload = json.loads(messages[1]["content"])
        payload["passages"][0]["article_type"] = "randomized trial"
        messages[1]["content"] = json.dumps(payload)
        with self.assertRaises(ValueError):
            verify_candidate_record(changed, question, cfg, [hit], "fixture-code")

    def test_course_message_layout_preserves_the_same_question_evidence_and_rules(self):
        cfg = mock_config(prompt="evidence_first")
        engine = Engine()
        prepared = prepare_context("Question with exact PHOX2B identifier", engine, cfg)
        old = run_request(prepared["question"], engine, cfg,
                          prepared_context=prepared, client=client())
        new = run_request(prepared["question"], engine, {**cfg, "prompt": "course_user"},
                          prepared_context=prepared, client=client())
        self.assertEqual(old["context_id"], new["context_id"])
        self.assertEqual(old["instructions"], new["instructions"])
        self.assertEqual(old["claims"], new["claims"])
        self.assertEqual(len(old["calls"][0]["messages"]), 2)
        messages = new["calls"][0]["messages"]
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["role"], "user")
        self.assertIn("QUESTION: " + prepared["question"], messages[0]["content"])
        self.assertIn("CONTEXT:\n" + new["context"], messages[0]["content"])
        self.assertNotIn("required_facts", messages[0]["content"])
        plain = run_request(prepared["question"], engine, {**cfg, "prompt": "plain_context"},
                            prepared_context=prepared, client=client())
        self.assertEqual(old["context_id"], plain["context_id"])
        self.assertEqual(old["instructions"], plain["instructions"])
        messages = plain["calls"][0]["messages"]
        self.assertEqual(messages[0], old["calls"][0]["messages"][0])
        self.assertIn("QUESTION: " + prepared["question"], messages[1]["content"])
        for passage in json.loads(old["context"]):
            for value in passage.values():
                self.assertIn(str(value), messages[1]["content"])
        self.assertNotIn("required_facts", messages[1]["content"])

    def test_candidate_prompt_planning_does_not_change_incumbent_or_final_split(self):
        incumbent = load_config()
        with patch("navigator.evaluation.read_documents", return_value=[]), \
             patch("navigator.evaluation.load_question_bank", return_value={"questions": [
                 {"id": "fixture", "split": "tuning", "answerable": True, "slice": "direct"}]}):
            plan = answer_plan(config=incumbent, prompt_names=["evidence_first", "coverage_first"])
            self.assertEqual(plan["prompts"], ["evidence_first", "coverage_first"])
            self.assertEqual(plan["maximum_generation_requests"], 2)
            self.assertEqual(incumbent["prompt"], load_config()["prompt"])
            for names in ([], ["unknown"], ["coverage_first", "coverage_first"]):
                with self.subTest(names=names), self.assertRaises(ValueError):
                    answer_plan(config=incumbent, prompt_names=names)
            for override in ({"prompt_names": ["coverage_first"]}, {"max_questions": 1},
                             {"question_ids": ["fixture"]}):
                with self.subTest(override=override), self.assertRaises(ValueError):
                    answer_plan(split="test", config=incumbent, **override)

    def setUp(self):
        self.cfg = mock_config()
        self.engine = Engine()

    def test_runtime_and_frozen_evaluation_have_same_context(self):
        prepared = prepare_context("question", self.engine, self.cfg, filters={"source_id": "fixture"})
        live = run_request("question", self.engine, self.cfg, filters={"source_id": "fixture"},
                           client=client(), traffic_origin="qa")
        reused = run_request("question", self.engine, {**self.cfg, "prompt": "concise"},
                             filters={"source_id": "fixture"}, prepared_context=prepared,
                             client=client(), traffic_origin="evaluation")
        self.assertEqual(live["context_id"], reused["context_id"])
        self.assertEqual(live["context"], reused["context"])
        self.assertEqual(live["retrieved_ids"], reused["retrieved_ids"])
        self.assertEqual(live["status"], "answered")
        self.assertEqual(reused["context_mode"], "frozen_reused")

    def test_frozen_context_cannot_be_changed_or_applied_to_other_question(self):
        prepared = prepare_context("question", self.engine, self.cfg)
        for change in ("text", "question", "policy"):
            candidate = copy.deepcopy(prepared)
            cfg = copy.deepcopy(self.cfg)
            question = "question"
            if change == "text":
                candidate["hits"][0]["content"] = "Changed"
            elif change == "question":
                question = "other"
            else:
                cfg["top_k"] = 1
            with self.subTest(change=change), self.assertRaises(ValueError):
                run_request(question, self.engine, cfg, prepared_context=candidate, client=client())

    def test_reused_rewrite_is_referenced_not_counted_twice(self):
        rewrite = {"query": "rewritten", "original_query": "question", "status": "rewritten",
                   "calls": [{"id": "attempt-1", "stage": "rewrite", "seconds": 0.01}]}
        with patch("navigator.rewriting.rewrite_query", return_value=copy.deepcopy(rewrite)):
            prepared = prepare_context("question", self.engine, self.cfg)
            live = run_request("question", self.engine, self.cfg, client=client())
        frozen = run_request("question", self.engine, self.cfg, prepared_context=prepared, client=client())
        self.assertEqual(self.engine.last[0], "rewritten")
        self.assertEqual(len(live["calls"]), 2)
        self.assertEqual(len(frozen["calls"]), 1)
        self.assertEqual(frozen["rewrite"]["calls"][0]["id"], "attempt-1")
        self.assertEqual(frozen["retrieval_seconds"], 0.0)

    def test_preview_never_calls_rewriter_or_generator(self):
        with patch("navigator.rewriting.rewrite_query", side_effect=AssertionError("model call")):
            record = run_request("question", self.engine, self.cfg, use_llm=False)
        self.assertEqual(record["status"], "preview")
        self.assertEqual(record["calls"], [])


class PlanTests(unittest.TestCase):
    def test_paired_evaluation_prepares_once_per_question_and_counts_actual_calls(self):
        docs = [copy.deepcopy(HIT)]
        questions = [{"id": "fixture-" + str(i), "split": "tuning", "slice": "direct",
                      "question": "Fictional question " + str(i), "answerable": True,
                      "reference_quotes": [], "required_facts": [], "required_qualifications": []}
                     for i in range(2)]
        engine = Engine()
        engine.corpus_id = digest(docs)
        with tempfile.TemporaryDirectory() as tmp, \
             patch("navigator.evaluation.ROOT", Path(tmp)), \
             patch("navigator.evaluation.read_documents", return_value=docs), \
             patch("navigator.evaluation.load_question_bank", return_value={"questions": questions}), \
             patch("navigator.evaluation.Retriever", return_value=engine), \
             patch.object(engine, "search", wraps=engine.search) as search:
            result = answer_evaluation(config=mock_config(), client=client())
            self.assertEqual(result["status"], "EXECUTED_AWAITING_REVIEW")
            self.assertEqual(search.call_count, 2)
            self.assertEqual(result["actual_provider_requests"], 4)
            self.assertEqual(len(result["per_question"]), 4)
            for q in questions:
                contexts = {r["record"]["context_id"] for r in result["per_question"] if r["question_id"] == q["id"]}
                self.assertEqual(len(contexts), 1)

    def test_six_question_pilot_covers_all_slices_and_test_has_one_prompt(self):
        with patch("navigator.evaluation.read_documents", return_value=prepare()[0]):
            pilot = answer_plan("tuning", 6)
            self.assertEqual(set(pilot["covered_slices"]), {
                "absent", "comparison", "direct", "exact_identifiers", "limitations", "paraphrase"})
            self.assertEqual(pilot["maximum_generation_requests"], 12)
            final = answer_plan("test")
            self.assertEqual(final["prompts"], [load_config()["prompt"]])
            self.assertEqual(final["maximum_provider_requests"], 18)

    def test_explicit_question_ids_cannot_cross_split_or_duplicate(self):
        with patch("navigator.evaluation.read_documents", return_value=prepare()[0]):
            selected = answer_plan("tuning", 6)["questions"]
            ids = [q["id"] for q in selected]
            self.assertEqual([q["id"] for q in answer_plan(question_ids=ids)["questions"]], ids)
            with self.assertRaises(ValueError):
                answer_plan(question_ids=ids + [ids[0]])
            with self.assertRaises(ValueError):
                answer_plan("test", question_ids=ids)

    def test_provider_failure_leaves_a_blocked_artifact_with_zero_attempts(self):
        with tempfile.TemporaryDirectory() as tmp, \
             patch("navigator.evaluation.ROOT", Path(tmp)), \
             patch("navigator.evaluation.read_documents", return_value=prepare()[0]), \
             patch("navigator.providers.model_identity", side_effect=RuntimeError("missing model")):
            # Keep the real bank reader's root while isolating newly written reports.
            from navigator.common import ROOT
            cfg = {**load_config(), "question_bank": str(ROOT / load_config()["question_bank"])}
            report = answer_evaluation("tuning", 6, config=cfg)
            self.assertEqual(report["status"], "BLOCKED_PREFLIGHT")
            self.assertEqual(report["actual_provider_requests"], 0)
            self.assertTrue((Path(tmp) / report["run_directory"] / "results.json").exists())

    def test_final_test_cannot_run_with_an_unselected_candidate(self):
        with self.assertRaises(ValueError):
            answer_evaluation("test", config={**load_config(),
                "generation_selection_status": "CANDIDATE_NOT_QUALITY_SELECTED"})


class CompletionAndCalibrationTests(unittest.TestCase):
    def test_blocked_and_incomplete_reports_exit_nonzero(self):
        for status in ("BLOCKED_MODEL_PREFLIGHT", "FAIL_OR_INCOMPLETE",
                       "EXECUTED_WITH_FAILED_VARIANTS_NO_SELECTION", "UNKNOWN",
                       "REVIEWED_INCOMPLETE_NO_SELECTION"):
            with self.subTest(status=status), contextlib.redirect_stdout(io.StringIO()), \
                 self.assertRaises(SystemExit) as raised:
                emit_report({"status": status})
            self.assertEqual(raised.exception.code, 1)

    def test_cli_propagates_matrix_failure(self):
        with patch("sys.argv", ["navigator", "evaluate-local-matrix", "--no-judge"]), \
             patch("navigator.experiments.generation_matrix",
                   return_value={"status": "BLOCKED_MODEL_PREFLIGHT"}), \
             contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as raised:
            main()
        self.assertEqual(raised.exception.code, 1)

    def test_completed_generation_is_not_mislabeled_as_quality_review(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            emit_report({"status": "EXECUTED_AWAITING_REVIEW"})
        self.assertIn("EXECUTED_AWAITING_REVIEW", output.getvalue())

    def test_changed_calibration_inputs_or_judge_rejected(self):
        from navigator.experiments import verify_calibration
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            fixtures = {"fixture": "fictional"}
            reviews = {"results_hash": digest(fixtures)}
            contract = {"model": "phi3", "digest": "fixture"}
            artifact = {"status": "PASS_FIXTURES_ONLY", "judge_contract": contract,
                        "fixtures_hash": digest(fixtures), "reviews_hash": digest(reviews),
                        "checks": {str(i): True for i in range(5)}}
            for name, value in [("fixtures", fixtures), ("reviews", reviews), ("calibration", artifact)]:
                (path / (name + ".json")).write_text(json.dumps(value))
            with patch("navigator.experiments.judge_contract", return_value=contract):
                self.assertEqual(verify_calibration(path / "calibration.json", {})["artifact_hash"], digest(artifact))
                (path / "fixtures.json").write_text('{"fixture":"tampered"}')
                with self.assertRaises(ValueError):
                    verify_calibration(path / "calibration.json", {})


class SelectionEvidenceTests(unittest.TestCase):
    def make_evidence(self, folder):
        # Synthetic receipt-shaped fixtures exercise validation; no model is called.
        documents = [copy.deepcopy(HIT)]
        question = {"id": "fixture", "question": "What was observed?", "split": "tuning",
                    "slice": "direct", "answerable": True,
                    "required_facts": [{"text": "Ten adults were observed."}],
                    "required_qualifications": []}
        bank = {"questions": [copy.deepcopy(question)]}
        cfg = mock_config(model_digest="fixture-digest")
        rows, judgments = [], []
        engine = Engine()
        engine.corpus_id = digest(documents)
        for prompt in ("concise", "evidence_first"):
            variant = {**cfg, "prompt": prompt}
            record = run_request(question["question"], engine, variant, client=client(), traffic_origin="evaluation")
            record["runtime_code_id"] = "fixture-code"
            # Simulate production-receipt fields only to test the selector's contract.
            # These temporary files are never delivered as live evaluation evidence.
            for call in record["calls"]:
                call.update(runtime_code_id="fixture-code", execution_kind="live_provider_client")
            row = {"question_id": question["id"], "answerable": True, "prompt": prompt,
                   "record": record, "record_hash": digest(record)}
            rows.append(row)
            judgments.append({"answer_id": record["id"], "record_hash": row["record_hash"],
                              "relevance": "relevant", "claim_support": ["supported"],
                              "fact_coverage": ["covered"], "qualification_coverage": [],
                              "abstention_correct": False, "reason": "Synthetic contract fixture."})
        results = {"status": "EXECUTED_AWAITING_REVIEW", "split": "tuning", "config": cfg,
                   "questions": [question], "questions_hash": digest(bank),
                   "corpus_id": digest(documents), "runtime_code_id": "fixture-code",
                   "prompts": ["concise", "evidence_first"], "per_question": rows}
        reviews = {"reviewer": "synthetic-validator-fixture", "reviewer_kind": "assistant",
                   "results_hash": digest(results), "reviews": judgments}
        rp, vp = folder / "results.json", folder / "reviews.json"
        rp.write_text(json.dumps(results))
        vp.write_text(json.dumps(reviews))
        write_whole_fixture(folder, results)
        return rp, vp, documents, bank, results

    def test_selected_config_verifies_until_config_or_evidence_changes(self):
        from navigator.experiments import select_generation
        from navigator.common import verify_generation_selection
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            rp, vp, documents, bank, _ = self.make_evidence(folder)
            with patch("navigator.experiments.ROOT", folder), \
                 patch("navigator.common.ROOT", folder), \
                 patch("navigator.experiments.runtime_code_id", return_value="fixture-code"), \
                 patch("navigator.common.runtime_code_id", return_value="fixture-code"), \
                 patch("navigator.experiments.read_documents", return_value=documents), \
                 patch("navigator.experiments.load_question_bank", return_value=bank):
                evidence = select_generation([rp], [vp], apply=True)
                selected = json.loads((folder / "configs/app.json").read_text())
                self.assertEqual(verify_generation_selection(selected)["winner"], evidence["winner"])
                with self.assertRaises(ValueError):
                    verify_generation_selection({**selected, "top_k": selected["top_k"] + 1})
                vp.write_text("{}")
                with self.assertRaises(ValueError):
                    verify_generation_selection(selected)

    def test_test_split_and_pilot_subset_cannot_select(self):
        from navigator.experiments import select_generation
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            rp, vp, documents, bank, results = self.make_evidence(folder)
            with patch("navigator.experiments.ROOT", folder), \
                 patch("navigator.experiments.runtime_code_id", return_value="fixture-code"), \
                 patch("navigator.experiments.read_documents", return_value=documents), \
                 patch("navigator.experiments.load_question_bank", return_value=bank):
                results["split"] = "test"
                rp.write_text(json.dumps(results))
                with self.assertRaises(ValueError):
                    select_generation([rp], [vp])
                results["split"] = "tuning"
                rp.write_text(json.dumps(results))
                bank["questions"].append({"id": "missing-from-pilot", "split": "tuning"})
                with self.assertRaises(ValueError):
                    select_generation([rp], [vp])

    def test_durable_attempt_is_written_before_the_sdk_attempt(self):
        from navigator.providers import complete
        cfg = mock_config()
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            def fail(**kwargs):
                artifacts = list((folder / "provider-attempts").glob("*.json"))
                self.assertEqual(len(artifacts), 1)
                self.assertEqual(json.loads(artifacts[0].read_text())["status"], "attempted")
                raise ConnectionError("fictional SDK outage")
            sdk = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=fail)))
            with patch("navigator.providers.runtime_dir", return_value=folder), \
                 patch("openai.OpenAI", return_value=sdk):
                ledger = []
                with self.assertRaises(ConnectionError):
                    complete(cfg, [{"role": "user", "content": "fictional fixture"}],
                             stage="generation", ledger=ledger)
            saved = json.loads(next((folder / "provider-attempts").glob("*.json")).read_text())
            self.assertEqual(saved["status"], "error")
            self.assertEqual(len(ledger), 1)
            self.assertEqual(saved["id"], ledger[0]["id"])
