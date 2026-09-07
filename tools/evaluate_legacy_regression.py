"""Recheck the 13 exposed questions, remapping exact quotes to current windows.

This is regression evidence, never a held-out score or a generation-quality test.
The original file and its historical split labels are preserved unchanged.
"""
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from navigator.common import ROOT, digest, load_config, read_documents, read_json, utc_now, write_json
from navigator.evaluation import metrics, validate_questions
from navigator.retrieval import Retriever

cfg, docs = load_config(), read_documents()
original = read_json(ROOT / "data/evaluation/questions.json")
questions, mappings = [], []
for old in original["questions"]:
    q = copy.deepcopy(old)
    q.update(split="regression_exposed", relevant_ids=[], reference_quotes=[])
    for ref in old["reference_quotes"]:
        source, version, passage, _, _ = ref["id"].split(":")
        matched = [d for d in docs if d["source_id"] == source
                   and d["source_version"].startswith(version)
                   and d["passage_index"] == int(passage) and ref["quote"] in d["content"]]
        if not matched:
            raise ValueError(f"Legacy quote no longer covered: {q['id']}")
        mappings.append({"question_id": q["id"], "original_reference": ref,
                         "current_ids": [d["id"] for d in matched]})
        q["reference_quotes"].extend({"id": d["id"], "quote": ref["quote"]} for d in matched)
        q["relevant_ids"].extend(d["id"] for d in matched)
    q["relevant_ids"] = list(dict.fromkeys(q["relevant_ids"]))
    questions.append(q)
validate_questions(questions, docs)
engine, rows = Retriever(docs, cfg), []
for method in ["lexical", "vector", "hybrid"]:
    for q in questions:
        hits = engine.search(q["question"], method=method)
        rows.append({"question_id": q["id"], "method": method,
                     "ranked_ids": [h["id"] for h in hits],
                     "metrics": metrics([h["id"] for h in hits], q["relevant_ids"]) if q["answerable"] else None})
report = {"status": "EXECUTED_EXPOSED_REGRESSION_ONLY", "created_at": utc_now(),
          "config": cfg, "config_id": digest(cfg), "corpus_id": digest(docs),
          "original_bank_hash": digest(original), "questions": questions,
          "quote_mappings": mappings, "rows": rows,
          "limitations": "Quote-bearing windows replace historical window IDs explicitly. Labels remain non-exhaustive and provisional. No model requests, no final v2 test, no configuration selection, no abstention quality claim."}
write_json(ROOT / "reports/remediation-v2/legacy-regression.json", report)
print({"status": report["status"], "questions": len(questions), "searches": len(rows)})
