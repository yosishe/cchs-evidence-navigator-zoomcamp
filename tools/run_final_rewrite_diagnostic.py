"""One declared, development-only rewrite diagnostic; never generation or promotion.

Calls the frozen course-derived rewrite/retrieval functions without modifying
their prompts or evaluators. The fixed IDs and time window are release-specific.
This is a project experiment adapter, not an additional course method.
"""
from pathlib import Path
import argparse
from datetime import datetime, timezone
import os
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from navigator.common import (ROOT, digest, effective_config, load_config,
                              read_documents, read_json, runtime_code_id,
                              runtime_dir, utc_now, write_json)
from navigator.evaluation import load_question_bank, metrics
from navigator.providers import model_identity
from navigator.retrieval import Retriever
from navigator.rewriting import protected_terms, rewrite_query

IDS = ("DIR-01", "DIR-02", "PAR-01", "PAR-02", "EXA-01", "EXA-02",
       "COM-01", "COM-02", "LIM-01", "LIM-02", "ABS-01", "ABS-02")
CONFIG_ID = "a608ccf3cd3318d9f54abb2c0d49a7967e920b4e841dded47f823d86884b2055"
CORPUS_ID = "a06955ab5c7a4f9c2d48213fae09980fe2628661f8ec5857527fe38d918dc7d0"
QUESTIONS_HASH = "f9981cd8ba660daa64ed05e7a5d98494b6d8ec6b1820a7291ee312100227b236"
CODE_ID = "5a8dff9b921a68fb270e2428144f8c24ccdc45c6458fdb7e14c40d5577d653cc"
START_BEFORE = datetime(2026, 9, 7, 20, 20, tzinfo=timezone.utc)
STOP_BEFORE = datetime(2026, 9, 7, 20, 50, tzinfo=timezone.utc)


def validate_inputs(plan, config, documents, bank):
    if tuple(plan["question_ids"]) != IDS:
        raise ValueError("Use only the twelve predeclared question IDs in order")
    if (digest(config) != CONFIG_ID or config.get("rewrite_enabled") is not False
            or digest(documents) != CORPUS_ID or digest(bank) != QUESTIONS_HASH
            or runtime_code_id() != CODE_ID):
        raise ValueError("A frozen identity or the disabled default changed")
    if (plan["config_id"] != CONFIG_ID or plan["corpus_id"] != CORPUS_ID
            or plan["questions_hash"] != QUESTIONS_HASH
            or plan["runtime_code_id"] != CODE_ID
            or plan["planned_rewrite_attempts"] != 12
            or plan["planned_searches"] != 24
            or plan["planned_generation_attempts"] != 0):
        raise ValueError("Declaration differs from the authorized diagnostic")
    lookup = {q["id"]: q for q in bank["questions"] if q["split"] == "tuning"}
    if not set(IDS) <= set(lookup):
        raise ValueError("A declared question is not in development")
    return [lookup[key] for key in IDS]


def score_search(hits, question, documents):
    ranked = [h["id"] for h in hits]
    wanted = set(question["relevant_ids"])
    source = {d["id"]: d["source_id"] for d in documents}
    required_sources = {source[key] for key in wanted}
    found_sources = {h["source_id"] for h in hits}
    return {
        "ranked_ids": ranked,
        "metrics": metrics(ranked, wanted) if question["answerable"] else None,
        "labeled_relevant_passages_found": len(wanted & set(ranked)),
        "labeled_relevant_passages_total": len(wanted),
        "labeled_source_coverage": {
            "required_sources": sorted(required_sources),
            "found_required_sources": sorted(required_sources & found_sources),
            "missing_required_sources": sorted(required_sources - found_sources),
            "scope": "Any returned passage from a labeled source; not fact completeness.",
        },
    }


def run(plan_path, documents_path, *, execute=False):
    plan_path, documents_path = Path(plan_path), Path(documents_path)
    output = ROOT / "reports/final/rewrite-diagnostic.json"
    if output.exists():
        raise ValueError("Diagnostic already started; no retries or overwrites")
    if not os.environ.get("NAVIGATOR_RUNTIME") or runtime_dir().resolve().is_relative_to(ROOT):
        raise ValueError("Use an explicitly separate runtime outside the repository")
    if list((runtime_dir() / "provider-attempts").glob("*.json")):
        raise ValueError("Use an empty diagnostic attempt journal")
    if any(os.environ.get(key) != "1" for key in ("HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE")):
        raise ValueError("Encoder use must be explicitly offline")
    if os.environ.get("ENABLE_PAID_LLM") != "0":
        raise ValueError("Paid execution must be explicitly disabled")
    config, plan = load_config(), read_json(plan_path)
    ingestion = read_json(documents_path.with_name("ingestion-report.json"))
    if digest(documents_path.read_bytes()) != ingestion["documents_sha256"]:
        raise ValueError("Prepared documents differ from their ingestion receipt")
    documents = read_documents(documents_path)
    bank = load_question_bank(config, documents)
    questions = validate_inputs(plan, config, documents, bank)
    if not execute:
        return {"status": "VALIDATED_WITHOUT_MODEL_OR_SEARCH_CALLS", "question_ids": list(IDS)}
    if datetime.now(timezone.utc) >= START_BEFORE:
        raise ValueError("The authorized start window has closed")
    report = {
        "status": "RUNNING", "started_at": utc_now(), "plan_hash": digest(plan),
        "runner_sha256": digest(Path(__file__).read_bytes()),
        "runtime_code_id": runtime_code_id(), "corpus_id": digest(documents),
        "questions_hash": digest(bank), "app_config": config,
        "app_config_id": digest(config), "effective_app_config_id": digest(effective_config(config)),
        "rewrite_call_config_id": digest({**config, "max_output_tokens": 256}),
        "question_ids": list(IDS), "rows": [], "actual_rewrite_attempts": 0,
        "search_attempts": 0, "actual_generation_attempts": 0,
        "enabled_in_submission": False,
        "semantic_intent_review": "PENDING_AGENT_REVIEW",
        "limitations": ["Development diagnostic with provisional, incomplete labels.",
                        "No generated-answer comparison and no final-test inference.",
                        "Identifier guards do not prove preserved semantic intent.",
                        "Raw-query ranks can improve even when a rewrite changes the task."],
    }

    def save():
        journals = sorted((runtime_dir() / "provider-attempts").glob("*.json"))
        receipts = [read_json(p) for p in journals]
        report["actual_rewrite_attempts"] = sum(r["stage"] == "rewrite" for r in receipts)
        report["actual_generation_attempts"] = sum(r["stage"] == "generation" for r in receipts)
        report["attempt_journal"] = receipts
        write_json(output, report)

    save()
    try:
        report["model_identity"] = model_identity(config)
        start = time.perf_counter()
        engine = Retriever(documents, config)
        engine.load_vectors(allow_download=False)
        report["retrieval_setup_seconds"] = time.perf_counter() - start
        for question in questions:
            if (STOP_BEFORE - datetime.now(timezone.utc)).total_seconds() <= config["request_timeout_seconds"] + 10:
                report["status"] = "PARTIAL_TIME_WINDOW_CLOSED"
                break
            row = {"question_id": question["id"], "question": question["question"],
                   "answerable": question["answerable"], "label_status": question["label_status"],
                   "semantic_intent_review": "PENDING_AGENT_REVIEW", "status": "STARTED"}
            report["rows"].append(row)
            row_start = time.perf_counter()
            for name in ("original", "rewritten"):
                if name == "rewritten":
                    start = time.perf_counter()
                    row["rewrite"] = rewrite_query(question["question"], config, enabled=True)
                    row["rewrite_seconds"] = time.perf_counter() - start
                    row["protected_terms"] = {
                        "original": sorted(protected_terms(question["question"])),
                        "guarded_query": sorted(protected_terms(row["rewrite"]["query"])),
                        "preserved": protected_terms(question["question"]) <= protected_terms(row["rewrite"]["query"]),
                    }
                    save()
                    calls = row["rewrite"]["calls"]
                    if len(calls) != 1 or any(c["stage"] != "rewrite" or c["status"] == "error" for c in calls):
                        row["status"] = "STOPPED_ON_PROVIDER_ERROR"
                        report["status"] = "STOPPED_ON_PROVIDER_ERROR"
                        break
                query = question["question"] if name == "original" else row["rewrite"]["query"]
                trace = {}
                report["search_attempts"] += 1
                save()
                start = time.perf_counter()
                hits = engine.search(query, trace=trace)
                seconds = time.perf_counter() - start
                row[name] = {**score_search(hits, question, documents), "trace": trace, "seconds": seconds}
                save()
            row["total_seconds"] = time.perf_counter() - row_start
            if report["status"] == "STOPPED_ON_PROVIDER_ERROR":
                break
            row["status"] = "COMPLETED_AWAITING_INTENT_REVIEW"
            save()
            print(f"Completed {row['question_id']}: {row['rewrite']['status']}", flush=True)
        else:
            report["status"] = "EXECUTED_AWAITING_INTENT_REVIEW"
    except BaseException as exc:
        report.update(status="STOPPED_ON_ERROR", error_type=type(exc).__name__)
        raise
    finally:
        report["completed_at"] = utc_now()
        save()
    if report["actual_rewrite_attempts"] > 12 or report["search_attempts"] > 24 or report["actual_generation_attempts"]:
        raise RuntimeError("Diagnostic exceeded its declared scope")
    return {key: report[key] for key in ("status", "actual_rewrite_attempts", "search_attempts", "actual_generation_attempts")}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan")
    parser.add_argument("--documents", required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    print(run(args.plan, args.documents, execute=args.execute))
