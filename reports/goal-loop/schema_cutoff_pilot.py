"""Iteration 028: schema on all saved missing-field pilot contexts; no retries."""
from pathlib import Path
import argparse
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from navigator.common import ROOT, digest, load_config, read_documents, read_json, runtime_code_id, utc_now, write_json
from navigator.evaluation import answer_evaluation
from navigator.preflight import inspect_runtime
from navigator.rag import OUTPUT_RULES, PROMPTS, build_context, generation_messages, retrieval_policy

PLAN = ROOT / "reports/goal-loop/iterations/028-schema-missing-fields.json"
DIRECTORY = ROOT / "reports/goal-loop/schema-cutoff-028"


def inputs():
    plan = read_json(PLAN)
    assert plan["runtime_code_id"] == runtime_code_id()
    assert plan["active_config_id"] == digest(load_config())
    assert plan["corpus_id"] == digest(read_documents())
    assert plan["question_bank_hash"] == digest(read_json(ROOT / "data/evaluation/questions-v2.json"))
    return plan


def prepare():
    plan = inputs()
    destination = DIRECTORY / "preparation.json"
    if destination.exists():
        raise FileExistsError("Do not overwrite completed preparation")
    canonical = {d["id"]: d for d in read_documents()}
    report = {"created_at": utc_now(), "status": "PREPARED_IDENTICAL_MESSAGES",
        "plan_hash": digest(plan), "script_hash": digest(Path(__file__).read_bytes()),
        "runtime_code_id": runtime_code_id(), "candidates": [], "fresh_retrieval_queries": 0,
        "model_calls": 0}
    for candidate in plan["candidates"]:
        baseline = read_json(ROOT / candidate["baseline_path"])
        assert digest(baseline) == candidate["baseline_hash"]
        cfg = candidate["config"]
        messages = {}
        for row in baseline["per_question"]:
            ctx = baseline["contexts"][row["question_id"]]
            assert digest({k: v for k, v in ctx.items() if k != "artifact_hash"}) == ctx["artifact_hash"]
            assert ctx["retrieval_policy"] == retrieval_policy(cfg)
            assert ctx["rewrite"]["calls"] == []
            assert build_context(ctx["hits"]) == build_context([canonical[h["id"]] for h in ctx["hits"]])
            messages[row["question_id"]] = generation_messages(ctx["question"], build_context(ctx["hits"]),
                PROMPTS["evidence_first"] + "\n" + OUTPUT_RULES, cfg)
            assert messages[row["question_id"]] == row["record"]["calls"][0]["messages"]
        report["candidates"].append({**candidate, "contexts": baseline["contexts"], "messages": messages})
    write_json(destination, report)
    print({"prepared_pairs": 8, "model_calls": 0}, flush=True)


def run():
    plan = inputs()
    prepared = read_json(DIRECTORY / "preparation.json")
    assert prepared["plan_hash"] == digest(plan)
    assert prepared["script_hash"] == digest(Path(__file__).read_bytes())
    destination = DIRECTORY / "execution.json"
    if destination.exists():
        raise FileExistsError("Inspect execution and live handle; do not repeat")
    preflight = inspect_runtime(prepared["candidates"][0]["config"])
    write_json(DIRECTORY / "preflight.json", preflight)
    assert preflight["status"] == "RUNTIME_METADATA_READY"
    assert preflight["selected_model"]["digest"] == plan["model"]["digest"]
    execution = {"created_at": utc_now(), "status": "RUNNING", "preparation_hash": digest(prepared),
        "runs": [], "actual_provider_requests": 0, "runtime_promoted": False, "official_points": None}
    write_json(destination, execution)
    try:
        for candidate in prepared["candidates"]:
            result = answer_evaluation(config=candidate["config"], question_ids=plan["question_ids"],
                prompt_names=plan["prompts"], prepared_contexts=candidate["contexts"])
            entry = {"id": candidate["id"], "result_path": result["run_directory"] + "/results.json",
                "result_hash": digest(result), "status": result["status"],
                "actual_provider_requests": result["actual_provider_requests"]}
            execution["runs"].append(entry)
            execution["actual_provider_requests"] += result["actual_provider_requests"]
            write_json(destination, execution)
            print(entry, flush=True)
            for row in result["per_question"]:
                call, = row["record"]["calls"]
                assert call["generation_json_schema"] is True
                assert call["messages"] == candidate["messages"][row["question_id"]]
                assert call["execution_kind"] == "live_provider_client"
                assert call["model_digest"] == plan["model"]["digest"]
            write_json(DIRECTORY / (candidate["id"] + "-postflight.json"), inspect_runtime(candidate["config"]))
            if result["status"] != "EXECUTED_AWAITING_REVIEW":
                execution["status"] = "STOPPED_ARM_FAILURE"
                break
        else:
            assert execution["actual_provider_requests"] == 8
            execution["status"] = "COMPLETED_AWAITING_REVIEW"
    except BaseException as exc:
        execution.update(status="STOPPED_ERROR", error_type=type(exc).__name__)
        raise
    finally:
        execution["completed_at"] = utc_now()
        write_json(destination, execution)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["prepare", "run"])
    args = parser.parse_args()
    (prepare if args.action == "prepare" else run)()
