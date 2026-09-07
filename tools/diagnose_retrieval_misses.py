"""Locate frozen development references in the current top-20 candidate pool.

No label edits, test-split evaluation, generation, download or config promotion.
This classifies known-reference rank failures, not all relevant biomedical evidence.
"""
import os
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from navigator.common import ROOT, digest, load_config, read_json, utc_now, write_json
from navigator.corpus import prepare
from navigator.evaluation import validate_questions
from navigator.exports import csv_export
from navigator.rag import retrieval_policy
from navigator.retrieval import Retriever


def run():
    cfg = load_config()
    docs, _, _ = prepare(cfg=cfg)
    bank = read_json(ROOT / cfg["question_bank"])
    questions = [q for q in bank["questions"] if q["split"] == "tuning"]
    validate_questions(questions, docs)
    if digest(docs) != bank["corpus_id"]:
        raise ValueError("Frozen labels do not match the active corpus")
    folder = ROOT / "reports/claude-remediation"
    prior = {k: os.environ.get(k) for k in ("NAVIGATOR_RUNTIME", "HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE")}
    os.environ.update(NAVIGATOR_RUNTIME=str(folder / "diagnostic-runtime"),
                      HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1")
    rows = []
    try:
        engine = Retriever(docs, cfg)
        for question in questions:
            if not question["answerable"]:
                continue
            hits = engine.search(question["question"], question.get("filters", {}), top_k=cfg["candidate_k"])
            positions = {hit["id"]: hit["rank"] for hit in hits}
            refs = []
            for ref in question["reference_quotes"]:
                found = [positions[i] for i in ref["acceptable_ids"] if i in positions]
                rank = min(found) if found else None
                diagnosis = ("in_final_context" if rank is not None and rank <= cfg["top_k"] else
                             "candidate_present_below_final_cutoff" if rank is not None else
                             "reference_not_in_candidate_pool")
                refs.append({"source_id": ref["source_id"], "quote": ref["quote"], "best_rank": rank,
                             "diagnosis": diagnosis, "acceptable_ids": ref["acceptable_ids"]})
            rows.append({"question_id": question["id"], "slice": question["slice"], "question": question["question"],
                         "hit_at_5": any(r["diagnosis"] == "in_final_context" for r in refs),
                         "fully_covered_at_5": all(r["diagnosis"] == "in_final_context" for r in refs),
                         "references": refs, "candidates": [{"id": h["id"], "rank": h["rank"]} for h in hits]})
        counts = Counter(ref["diagnosis"] for row in rows for ref in row["references"])
        report = {"status": "EXECUTED_PROVISIONAL_LABELS", "created_at": utc_now(),
                  "config_id": digest(cfg), "retrieval_policy": retrieval_policy(cfg), "corpus_id": digest(docs),
                  "question_bank_hash": digest(bank), "split": "tuning", "searches": len(rows),
                  "generation_calls": 0, "test_evaluated": False, "configuration_promoted": False,
                  "reference_diagnoses": dict(counts), "answerable_questions": len(rows),
                  "no_reference_hit": sum(not r["hit_at_5"] for r in rows),
                  "incomplete_reference_coverage": sum(not r["fully_covered_at_5"] for r in rows),
                  "limitations": "Frozen provisional reference labels are not exhaustive. All referenced quotations exist in the corpus; this does not audit unlabeled, excluded or missing literature. A reranker can only reorder present candidates.",
                  "per_question": rows}
        write_json(folder / "retrieval-misses.json", report)
        flat = [{"question_id": row["question_id"], "slice": row["slice"], "question": row["question"],
                 "source_id": ref["source_id"], "reference_quote": ref["quote"],
                 "best_candidate_rank": ref["best_rank"], "diagnosis": ref["diagnosis"]}
                for row in rows for ref in row["references"] if ref["diagnosis"] != "in_final_context"]
        (folder / "retrieval-misses.csv").write_text(csv_export(flat))
        print({k: v for k, v in report.items() if k not in {"per_question", "retrieval_policy"}})
    finally:
        for key, value in prior.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


if __name__ == "__main__":
    run()
