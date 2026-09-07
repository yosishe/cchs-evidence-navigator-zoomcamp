"""Bounded release experiments. Plans and results are separate, never auto-selected.

Uses existing course-derived ingestion, retrieval and Chat Completions interfaces.
No model downloads, package installation, paid calls, judge calls or retries.
"""
from pathlib import Path
import argparse
import copy
import json
import platform
import sys
import time
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from navigator.common import ROOT, digest, load_config, read_documents, read_json, runtime_code_id, utc_now, write_json
from navigator.evaluation import answer_evaluation, load_question_bank, metrics
from navigator.providers import model_identity, OWNER_MODEL_EXCEPTIONS
from navigator.rag import prepare_context, run_request
from navigator.retrieval import Retriever

OUT = ROOT / "reports/release-quality"
MODELS = ["phi3", "gemma3:12b"]
PROMPTS = ["evidence_first", "numbered_evidence"]


def metadata():
    import requests
    session = requests.Session(); session.trust_env = False
    report = {"observed_at": utc_now(), "python_version": platform.python_version()}
    for endpoint in ("version", "ps"):
        response = session.get("http://127.0.0.1:11434/api/" + endpoint, timeout=10,
                               allow_redirects=False)
        response.raise_for_status(); report[endpoint] = response.json()
    return report


def plan():
    target = OUT / "pilot-plan.json"
    if target.exists():
        raise ValueError("Plan already frozen; use a new declared iteration instead of overwriting")
    cfg = {**load_config(), "request_timeout_seconds": 300,
           "generation_json_schema": False, "json_mode": True, "rewrite_enabled": False}
    docs = read_documents(); bank = load_question_bank(cfg, docs)
    questions = [q for q in bank["questions"] if q["split"] == "tuning"]
    used = Counter(); selected = []
    for q in questions:
        if used[q["slice"]] < 2:
            selected.append(q["id"]); used[q["slice"]] += 1
    if len(selected) != 12 or set(used.values()) != {2}:
        raise ValueError("Pilot requires exactly two development questions per six slices")
    variants = []
    for model in MODELS:
        for prompt in PROMPTS:
            variant = {**cfg, "model": model, "prompt": prompt}
            if model in OWNER_MODEL_EXCEPTIONS:
                variant["model_digest"] = OWNER_MODEL_EXCEPTIONS[model]
            variants.append({"arm": f"arm-{len(variants)+1}", "config": variant})
    result = {"status": "PLANNED_NOT_EXECUTED", "created_at": utc_now(),
        "runtime_code_id": runtime_code_id(), "corpus_id": digest(docs),
        "questions_hash": digest(bank), "question_ids": selected, "slices": dict(used),
        "variants": variants, "planned_generation_attempts": 48,
        "feasibility": {"question_id": selected[0], "models": MODELS,
            "prompt": "numbered_evidence", "planned_attempts": 2,
            "purpose": "Capacity/format observations only; excluded from pilot quality totals"},
        "fixed_conditions": "Same context artifacts, vector/5, max output 900, temperature 0, timeout 300 s, JSON object mode; no retries or paid fallback. The timeout is an execution bound, not a course threshold.",
        "continuation_gate": "At least one complete supported answerable pilot response; inspect every slice and all whole-answer/critical regressions before broadening. Partial-coverage diagnostics cannot nominate a winner or bypass the original quality contract.",
        "full_development_gate": "Compare two justified generation alternatives across all 42 development questions with identical chosen retrieval contexts. No automatic promotion.",
        "final_test": "No final-set inference in this pilot; exposed/validated bank is not a blind test."}
    write_json(target, result); print(json.dumps(result, indent=2), flush=True)


def frozen_plan():
    result = read_json(OUT / "pilot-plan.json")
    if result["runtime_code_id"] != runtime_code_id():
        raise ValueError("Runtime code changed after pilot plan; declare a new iteration")
    docs = read_documents(); bank = load_question_bank(result["variants"][0]["config"], docs)
    if digest(docs) != result["corpus_id"] or digest(bank) != result["questions_hash"]:
        raise ValueError("Protected corpus or benchmark changed")
    return result, docs, bank


def feasibility():
    declaration, docs, bank = frozen_plan()
    target = OUT / "feasibility.json"
    if target.exists(): raise ValueError("Feasibility already attempted; never silently reroll")
    q = next(q for q in bank["questions"] if q["id"] == declaration["feasibility"]["question_id"])
    cfg = declaration["variants"][0]["config"]
    engine = Retriever(docs, cfg)
    prepared = prepare_context(q["question"], engine, cfg, filters=q.get("filters", {}))
    result = {"status": "RUNNING", "created_at": utc_now(), "plan_hash": digest(declaration),
              "scope": "Feasibility, not a quality selection experiment", "before": metadata(),
              "question_id": q["id"], "records": [], "actual_attempts": 0}
    write_json(target, result)
    for model in MODELS:
        variant = {**cfg, "model": model, "prompt": "numbered_evidence"}
        variant["model_digest"] = model_identity(variant)["digest"]
        rec = run_request(q["question"], engine, variant, prepared_context=prepared,
                          filters=q.get("filters", {}), traffic_origin="evaluation")
        result["records"].append({"record": rec, "after": metadata()})
        result["actual_attempts"] += len(rec["calls"])
        write_json(target, result)
        print(json.dumps({"model": model, "status": rec["status"], "seconds": rec["seconds"],
                          "input_tokens": rec["input_tokens"], "output_tokens": rec["output_tokens"]}), flush=True)
        if rec["status"] == "error" and rec.get("error_stage") != "output_validation":
            result["status"] = "STOPPED_INFRASTRUCTURE"; write_json(target, result); return
    result["status"] = "EXECUTED_FEASIBILITY_ONLY"; write_json(target, result)


def pilot():
    declaration, docs, bank = frozen_plan()
    target = OUT / "pilot-index.json"
    if target.exists(): raise ValueError("Pilot has already started; inspect its terminal/live state")
    feasibility = read_json(OUT / "feasibility.json")
    if feasibility["status"] != "EXECUTED_FEASIBILITY_ONLY":
        raise ValueError("Infrastructure feasibility is incomplete")
    cfg = declaration["variants"][0]["config"]; engine = Retriever(docs, cfg)
    questions = {q["id"]: q for q in bank["questions"] if q["split"] == "tuning"}
    contexts = {key: prepare_context(questions[key]["question"], engine, cfg,
                filters=questions[key].get("filters", {})) for key in declaration["question_ids"]}
    write_json(OUT / "pilot-contexts.json", contexts)
    result = {"status": "RUNNING", "created_at": utc_now(), "plan_hash": digest(declaration),
              "context_hash": digest(contexts), "arms": [], "actual_attempts": 0}
    write_json(target, result)
    for arm in declaration["variants"]:
        print("Starting " + arm["arm"], flush=True)
        report = answer_evaluation(config=arm["config"], question_ids=declaration["question_ids"],
                  prepared_contexts=contexts, prompt_names=[arm["config"]["prompt"]])
        result["arms"].append({"arm": arm["arm"], "status": report["status"],
                              "results_path": report["run_directory"] + "/results.json",
                              "actual_attempts": report["actual_provider_requests"], "after": metadata()})
        result["actual_attempts"] += report["actual_provider_requests"]
        write_json(target, result)
        print(json.dumps(result["arms"][-1]), flush=True)
        if report["status"] != "EXECUTED_AWAITING_REVIEW":
            result["status"] = "STOPPED_INCOMPLETE"; write_json(target, result); return
    result["status"] = "EXECUTED_AWAITING_AGENT_REVIEW"; write_json(target, result)


def retrieval():
    target = OUT / "retrieval-factorial.json"
    if target.exists(): raise ValueError("Retrieval experiment exists; do not overwrite evidence")
    cfg = load_config(); docs = read_documents(); bank = load_question_bank(cfg, docs)
    questions = [q for q in bank["questions"] if q["split"] == "tuning"]
    result = {"status": "RUNNING", "created_at": utc_now(), "runtime_code_id": runtime_code_id(),
        "corpus_id": digest(docs), "questions_hash": digest(bank), "split": "tuning",
        "actual_provider_requests": 0, "planned_searches": 168, "actual_searches": 0, "arms": [],
        "selection_rule": "Reference coverage first, then Hit/MRR; inspect all losses before a candidate proceeds. Answer quality still required. RRF constant 50, zero-based rank; candidate pool and boosts unchanged."}
    write_json(target, result)
    engine = Retriever(docs, cfg); engine.load_vectors()
    for method in ["vector", "hybrid"]:
        for top_k in [5, 10]:
            variant = {**cfg, "retrieval": method, "top_k": top_k}; engine.config = variant
            rows = []
            for q in questions:
                trace = {}; start = time.perf_counter()
                hits = engine.search(q["question"], filters=q.get("filters", {}), method=method, trace=trace)
                ids = [hit["id"] for hit in hits]
                refs = q.get("reference_quotes", [])
                covered = [any(key in ref.get("acceptable_ids", [ref["id"]]) for key in ids) for ref in refs]
                rows.append({"id": q["id"], "slice": q["slice"], "answerable": q["answerable"],
                    "ranked_ids": ids, "reference_covered": covered,
                    "reference_coverage": sum(covered)/len(covered) if covered else None,
                    "metrics": metrics(ids, q["relevant_ids"]) if q["answerable"] else None,
                    "seconds": time.perf_counter()-start, "trace": trace})
                result["actual_searches"] += 1
            eligible = [row for row in rows if row["answerable"]]
            arm = {"method": method, "top_k": top_k, "config": variant, "per_question": rows,
                "answerable_denominator": len(eligible),
                "fully_covered": sum(row["reference_coverage"] == 1 for row in eligible),
                "mean_reference_coverage": sum(row["reference_coverage"] for row in eligible)/len(eligible),
                "hit_at_k": sum(row["metrics"]["hit"] for row in eligible)/len(eligible),
                "mrr_at_k": sum(row["metrics"]["reciprocal_rank"] for row in eligible)/len(eligible)}
            result["arms"].append(arm); write_json(target, result)
            print(json.dumps({k:v for k,v in arm.items() if k not in {"config", "per_question"}}), flush=True)
    result["status"] = "EXECUTED_PROVISIONAL_LABELS_NO_PROMOTION"; write_json(target, result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["plan", "feasibility", "pilot", "retrieval"])
    args = parser.parse_args()
    globals()[args.action]()
