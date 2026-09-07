"""Validate explicitly authored judgments and bind them to immutable run artifacts.

This does not judge model answers. The assistant must inspect the actual outputs,
sources and exports before writing every judgment; missing entries are rejected.
"""
from pathlib import Path
import argparse
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from navigator.common import ROOT, digest, read_json, write_json
from navigator.evaluation import summarize_answer_review
from navigator.whole_review import whole_review_template, apply_whole_review


def materialize(results_path, judgments_path):
    results_path, judgments_path = Path(results_path), Path(judgments_path)
    result, notes = read_json(results_path), read_json(judgments_path)
    if result["status"] != "EXECUTED_AWAITING_REVIEW":
        raise ValueError("Review completion requires a terminal completed experiment")
    if notes["results_hash"] != digest(result):
        raise ValueError("Manual judgments do not match this exact result")
    lookup = {q["id"]: q for q in result["questions"]}
    if set(notes["questions"]) != set(lookup):
        raise ValueError("Every planned question needs an explicit inspected judgment")
    if len(result["prompts"]) != 1:
        raise ValueError("One arm per manually authored judgment file")
    reviews = {"reviewer": "Codex source-based provisional assistant review",
               "reviewer_kind": "assistant", "results_hash": digest(result), "reviews": []}
    whole = whole_review_template(result)
    whole.update(reviewer=reviews["reviewer"], reviewer_kind="assistant")
    for row, w in zip(result["per_question"], whole["reviews"]):
        note = notes["questions"][row["question_id"]]
        review = {key: note[key] for key in ["relevance", "claim_support", "abstention_correct",
                   "fact_coverage", "qualification_coverage", "reason"]}
        review.update(answer_id=row["record"]["id"], record_hash=row["record_hash"])
        reviews["reviews"].append(review)
        w.update({key: note[key] for key in ["visible_prose_supported",
                   "export_preserves_qualifications", "critical_failures", "reason"]})
    primary = summarize_answer_review(result, reviews)
    verdicts = {d["answer_id"]: d["acceptable"] for d in primary["per_question"]}
    for w in whole["reviews"]:
        w["acceptable"] = bool(verdicts[w["answer_id"]] and w["visible_prose_supported"] is True
                               and w["export_preserves_qualifications"] is True and not w["critical_failures"])
    summary = apply_whole_review(result, primary, whole)
    parent = results_path.parent
    for name in ["reviews.json", "whole-answer-review.json", "review-summary.json"]:
        if (parent / name).exists():
            raise ValueError("Do not overwrite an existing reviewed version")
    write_json(parent / "reviews.json", reviews)
    write_json(parent / "whole-answer-review.json", whole)
    write_json(parent / "review-summary.json", summary)
    print(summary["aggregates"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("results"); parser.add_argument("judgments")
    args = parser.parse_args(); materialize(args.results, args.judgments)
