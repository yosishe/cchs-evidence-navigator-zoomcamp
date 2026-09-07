"""Known-error review challenges; these are not live model-quality results."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from navigator.common import digest, verify_generation_selection
from navigator.evaluation import summarize_answer_review
from navigator.experiments import select_generation
from navigator.whole_review import apply_whole_review
import test_core_completion as fixtures


class WholeReviewTests(unittest.TestCase):
    def mixed_abstention_evidence(self, answerable_winner=None):
        """Synthetic mixed bank; never written as real model/clinical evidence."""
        from navigator.rag import run_request
        first = copy.deepcopy(self.results["questions"][0])
        absent = {**first, "id": "fixture-absent", "question": "What was the unreported outcome?",
                  "slice": "absent", "answerable": False, "required_facts": []}
        self.bank = {"questions": [first, absent]}
        cfg = self.results["config"]
        engine = fixtures.Engine()
        engine.corpus_id = digest(self.docs)
        rows, reviews, verdicts = [], [], []
        for question in self.bank["questions"]:
            for prompt in self.results["prompts"]:
                successful = question["answerable"] and prompt == answerable_winner
                payload = fixtures.PAYLOAD if successful else {
                    "status": "insufficient_evidence", "claims": [],
                    "limitations": "No sourced answer was produced in this synthetic fixture."}
                with patch.object(fixtures, "PAYLOAD", payload):
                    record = run_request(question["question"], engine, {**cfg, "prompt": prompt},
                                         client=fixtures.client(), traffic_origin="evaluation")
                record["runtime_code_id"] = "fixture-code"
                for call in record["calls"]:
                    call.update(runtime_code_id="fixture-code", execution_kind="live_provider_client")
                rows.append({"question_id": question["id"], "answerable": question["answerable"],
                             "prompt": prompt, "record": record, "record_hash": digest(record)})
                acceptable = successful or not question["answerable"]
                verdicts.append(acceptable)
                reviews.append({"answer_id": record["id"], "record_hash": digest(record),
                    "relevance": "relevant" if acceptable else "not_relevant",
                    "claim_support": ["supported"] if successful else [],
                    "fact_coverage": (["covered"] if successful else ["missing"]) if question["answerable"] else [],
                    "qualification_coverage": [], "abstention_correct": not question["answerable"],
                    "reason": "Synthetic mixed-bank contract fixture, no scientific judgment."})
        self.results.update(questions=self.bank["questions"], questions_hash=digest(self.bank), per_question=rows)
        self.reviews.update(results_hash=digest(self.results), reviews=reviews)
        self.whole = fixtures.write_whole_fixture(self.folder, self.results, verdicts)
        self.rp.write_text(json.dumps(self.results))
        self.vp.write_text(json.dumps(self.reviews))

    def select_fixture(self):
        with patch("navigator.experiments.ROOT", self.folder), \
             patch("navigator.experiments.runtime_code_id", return_value="fixture-code"), \
             patch("navigator.experiments.read_documents", return_value=self.docs), \
             patch("navigator.experiments.load_question_bank", return_value=self.bank):
            return select_generation([self.rp], [self.vp])

    def test_mixed_bank_all_abstention_is_not_a_usable_winner(self):
        self.mixed_abstention_evidence()
        primary = summarize_answer_review(self.results, self.reviews)
        self.assertEqual([a["acceptable_answers"] for a in primary["aggregates"]], [1, 1])
        self.assertEqual(primary["eligible_best_prompts"], [])
        self.assertEqual(self.summary()["eligible_best_prompts"], [])
        with self.assertRaisesRegex(ValueError, "answerable"):
            self.select_fixture()

    def test_mixed_bank_supported_answerable_candidate_remains_selectable(self):
        self.mixed_abstention_evidence(answerable_winner="evidence_first")
        self.assertEqual(self.summary()["eligible_best_prompts"], ["evidence_first"])
        self.assertEqual(self.select_fixture()["winner"]["prompt"], "evidence_first")

    def test_whole_answer_veto_cannot_leave_only_refusals_as_a_winner(self):
        self.mixed_abstention_evidence(answerable_winner="evidence_first")
        self.whole["reviews"][1].update(visible_prose_supported=None, acceptable=False)
        (self.folder / "whole-answer-review.json").write_text(json.dumps(self.whole))
        self.assertEqual(self.summary()["eligible_best_prompts"], [])
        with self.assertRaisesRegex(ValueError, "answerable"):
            self.select_fixture()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.rp, self.vp, self.docs, self.bank, self.results = fixtures.SelectionEvidenceTests().make_evidence(self.folder)
        self.reviews = json.loads(self.vp.read_text())
        self.whole = json.loads((self.folder / "whole-answer-review.json").read_text())

    def summary(self, whole=None):
        return apply_whole_review(self.results, summarize_answer_review(self.results, self.reviews),
                                  self.whole if whole is None else whole)

    def test_supported_claims_do_not_override_unsupported_visible_prose(self):
        self.whole["reviews"][0].update(visible_prose_supported=False, acceptable=False,
                                       critical_failures=["Fictional unsupported premise in limitations"])
        summary = self.summary()
        self.assertEqual([r["acceptable_answers"] for r in summary["aggregates"]], [0, 1])
        self.assertEqual(summary["eligible_best_prompts"], ["evidence_first"])
        self.assertEqual(summary["aggregates"][0]["critical_failure_answers"], 1)

    def test_unknown_does_not_pass_and_sidecar_cannot_upgrade_incomplete_answer(self):
        self.whole["reviews"][0].update(visible_prose_supported=None, acceptable=False)
        self.assertFalse(self.summary()["per_question"][0]["acceptable"])
        self.reviews["reviews"][1]["fact_coverage"] = ["missing"]
        with self.assertRaisesRegex(ValueError, "cannot override"):
            self.summary()

    def test_missing_duplicate_foreign_changed_and_nonboolean_reviews_rejected(self):
        cases = []
        for name in ("missing", "duplicate", "foreign", "hash", "export", "boolean", "reason"):
            w = copy.deepcopy(self.whole)
            if name == "missing": w["reviews"].pop()
            elif name == "duplicate": w["reviews"].append(copy.deepcopy(w["reviews"][0]))
            elif name == "foreign": w["reviews"][0]["answer_id"] = "foreign"
            elif name == "hash": w["reviews"][0]["record_hash"] = "changed"
            elif name == "export": w["reviews"][0]["export_hash"] = "changed"
            elif name == "boolean": w["reviews"][0]["visible_prose_supported"] = 1
            else: w["reviews"][0]["reason"] = " "
            cases.append((name, w))
        for name, w in cases:
            with self.subTest(case=name), self.assertRaises(ValueError): self.summary(w)

    def test_selection_and_runtime_require_the_same_whole_answer_artifact(self):
        with patch("navigator.experiments.ROOT", self.folder), patch("navigator.common.ROOT", self.folder), \
             patch("navigator.experiments.runtime_code_id", return_value="fixture-code"), \
             patch("navigator.common.runtime_code_id", return_value="fixture-code"), \
             patch("navigator.experiments.read_documents", return_value=self.docs), \
             patch("navigator.experiments.load_question_bank", return_value=self.bank):
            selected = select_generation([self.rp], [self.vp], apply=True)
            cfg = selected["selected_config"]
            self.assertEqual(verify_generation_selection(cfg)["status"], "SELECTED_ON_PROVISIONAL_AGENT_REVIEW")
            path = self.folder / "whole-answer-review.json"
            path.write_text("{}")
            with self.assertRaises(ValueError): verify_generation_selection(cfg)
            with self.assertRaises(ValueError): select_generation([self.rp], [self.vp])
            path.unlink()
            with self.assertRaisesRegex(ValueError, "whole-answer-review"):
                select_generation([self.rp], [self.vp])

    def test_all_abstention_cannot_pass_answerable_questions(self):
        for row, review in zip(self.results["per_question"], self.reviews["reviews"]):
            row["record"].update(status="insufficient_evidence", claims=[])
            row["record_hash"] = digest(row["record"])
            review.update(record_hash=row["record_hash"], claim_support=[], fact_coverage=["missing"],
                          abstention_correct=True)
        self.reviews["results_hash"] = digest(self.results)
        self.whole = fixtures.write_whole_fixture(self.folder, self.results, [False, False])
        self.assertEqual(self.summary()["eligible_best_prompts"], [])

    def test_selector_rejects_when_every_candidate_has_a_critical_failure(self):
        # Both alternatives fail the veto, so a recorded correct claim is insufficient.
        for row in self.whole["reviews"]:
            row.update(visible_prose_supported=False, acceptable=False)
        (self.folder / "whole-answer-review.json").write_text(json.dumps(self.whole))
        with patch("navigator.experiments.ROOT", self.folder), \
             patch("navigator.experiments.runtime_code_id", return_value="fixture-code"), \
             patch("navigator.experiments.read_documents", return_value=self.docs), \
             patch("navigator.experiments.load_question_bank", return_value=self.bank), \
             self.assertRaisesRegex(ValueError, "critical"):
            select_generation([self.rp], [self.vp])


if __name__ == "__main__":
    unittest.main()
