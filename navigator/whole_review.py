"""Enforce explicit whole-answer judgments; no automatic semantic truth claim.

Project adaptation of course Module 4 paired review. Review records and current
export payloads are bound together so selection cannot omit the narrative veto.
"""
from __future__ import annotations

import copy
from .common import digest
from .exports import comparison_rows, tag_proposal_rows


def export_payload(record):
    return {"comparison_rows": comparison_rows(record),
            "tag_proposal_rows": tag_proposal_rows(record)}


def whole_review_template(results):
    return {"schema_version": 1, "reviewer": "", "reviewer_kind": "",
            "results_hash": digest(results), "reviews": [
                {"answer_id": row["record"]["id"], "record_hash": row["record_hash"],
                 "export_hash": digest(export_payload(row["record"])),
                 "visible_prose_supported": None,
                 "export_preserves_qualifications": None,
                 "critical_failures": [], "acceptable": None, "reason": ""}
                for row in results["per_question"]]}


def apply_whole_review(results, base_summary, whole):
    """Combine explicit judgments with primary review, never upgrade its verdict.

    Booleans are reviewer assertions, not machine proof of entailment. Unknown
    judgments stay unacceptable. Hashes detect inconsistency, not rehashed forgery.
    """
    if (whole.get("schema_version") != 1 or whole.get("results_hash") != digest(results)
            or not isinstance(whole.get("reviewer"), str) or not whole["reviewer"].strip()
            or whole.get("reviewer_kind") != "assistant"):
        raise ValueError("A versioned whole-answer artifact with explicit assistant review is required")
    rows = {r["record"]["id"]: r for r in results["per_question"]}
    entries = whole.get("reviews")
    if not isinstance(entries, list):
        raise ValueError("Whole-answer reviews must be a list")
    judgments = {r["answer_id"]: r for r in entries}
    if len(judgments) != len(entries) or set(judgments) != set(rows):
        raise ValueError("Missing, duplicate or foreign whole-answer review")
    summary = copy.deepcopy(base_summary)
    for detail in summary["per_question"]:
        row = rows[detail["answer_id"]]
        review = judgments[detail["answer_id"]]
        if (review.get("record_hash") != digest(row["record"])
                or review.get("export_hash") != digest(export_payload(row["record"]))):
            raise ValueError("Whole-answer review differs from the answer or current export")
        for key in ("visible_prose_supported", "export_preserves_qualifications"):
            if review.get(key) is not None and type(review[key]) is not bool:
                raise ValueError("Whole-answer judgments must be boolean or explicit unknown")
            if key not in review:
                raise ValueError("Missing whole-answer judgment")
        failures = review.get("critical_failures")
        if (not isinstance(failures, list) or
                any(not isinstance(f, str) or not f.strip() for f in failures)
                or not isinstance(review.get("reason"), str) or not review["reason"].strip()):
            raise ValueError("Explicit critical failures and source-based reason are required")
        approved = (detail["acceptable"] and review["visible_prose_supported"] is True
                    and review["export_preserves_qualifications"] is True and not failures)
        if type(review.get("acceptable")) is not bool or review["acceptable"] != approved:
            raise ValueError("Whole-answer verdict cannot override a primary rejection or failed veto")
        detail.update(acceptable=approved,
                      visible_prose_supported=review["visible_prose_supported"],
                      export_preserves_qualifications=review["export_preserves_qualifications"],
                      whole_answer_reason=review["reason"],
                      whole_answer_critical=(bool(failures) or review["visible_prose_supported"] is False
                                             or review["export_preserves_qualifications"] is False))
    for aggregate in summary["aggregates"]:
        subset = [r for r in summary["per_question"] if r["prompt"] == aggregate["prompt"]]
        aggregate["acceptable_answers"] = sum(r["acceptable"] for r in subset)
        aggregate["acceptable_rate"] = aggregate["acceptable_answers"] / len(subset) if subset else None
        aggregate["critical_failure_answers"] = sum(r["whole_answer_critical"] for r in subset)
    for aggregate in summary["per_slice"]:
        subset = [r for r in summary["per_question"]
                  if r["prompt"] == aggregate["prompt"] and r["slice"] == aggregate["slice"]]
        aggregate["acceptable_answers"] = sum(r["acceptable"] for r in subset)
        aggregate["acceptable_rate"] = aggregate["acceptable_answers"] / len(subset) if subset else None
    answered_prompts = {d["prompt"] for d in summary["per_question"]
                        if d["answerable"] and d["acceptable"]}
    viable = [a for a in summary["aggregates"] if a["prompt"] in answered_prompts
              and not a["critical_failure_answers"] and not a["unsupported_claims"]]
    best = max((a["acceptable_rate"] for a in viable), default=None)
    summary["eligible_best_prompts"] = [a["prompt"] for a in viable if a["acceptable_rate"] == best] if (
        summary["status"] == "REVIEWED_COMPLETE" and results.get("split") == "tuning") else []
    summary.update(whole_answer_reviewed=True, whole_reviews_hash=digest(whole),
                   whole_answer_reviewer=whole["reviewer"],
                   whole_answer_note="Explicit assistant judgments and export consistency, not clinical validation")
    return summary
