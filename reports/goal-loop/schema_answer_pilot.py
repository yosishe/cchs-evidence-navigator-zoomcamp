"""Iteration 027: one six-call schema experiment; never reroll completed outputs."""
from pathlib import Path
import argparse
import copy
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from navigator.common import ROOT, digest, load_config, read_documents, read_json, runtime_code_id, utc_now, write_json
from navigator.evaluation import answer_evaluation
from navigator.preflight import inspect_runtime
from navigator.rag import OUTPUT_RULES, PROMPTS, build_context, generation_messages, retrieval_policy

DIRECTORY = ROOT / "reports/goal-loop/schema-answer-027"
PLAN = ROOT / "reports/goal-loop/iterations/027-schema-constrained-generation.json"


def prepare():
    destination = DIRECTORY / "preparation.json"
    if destination.exists():
        raise FileExistsError("Inspect the completed preparation; no silent replacement")
    plan = read_json(PLAN)
    baseline = read_json(ROOT / plan["baseline_path"])
    assert digest(baseline) == plan["baseline_hash"]
    assert digest(load_config()) == plan["active_config_id"]
    documents = read_documents()
    assert digest(documents) == plan["corpus_id"]
    assert digest(read_json(ROOT / "data/evaluation/questions-v2.json")) == plan["question_bank_hash"]
    cfg = {**baseline["config"], **plan["config_change"]}
    contexts = copy.deepcopy(baseline["contexts"])
    canonical = {d["id"]: d for d in documents}
    messages = {}
    for row in baseline["per_question"]:
        qid, prompt = row["question_id"], row["prompt"]
        ctx = contexts[qid]
        checked = {k: v for k, v in ctx.items() if k != "artifact_hash"}
        assert digest(checked) == ctx["artifact_hash"]
        assert ctx["retrieval_policy"] == retrieval_policy(cfg)
        assert ctx["corpus_id"] == plan["corpus_id"]
        assert ctx["rewrite"]["calls"] == []
        # Exact text/identity/metadata of every saved hit must still be canonical.
        assert build_context(ctx["hits"]) == build_context([canonical[h["id"]] for h in ctx["hits"]])
        variant = {**cfg, "prompt": prompt}
        msg = generation_messages(ctx["question"], build_context(ctx["hits"]),
                                  PROMPTS[prompt] + "\n" + OUTPUT_RULES, variant)
        assert msg == row["record"]["calls"][0]["messages"]
        messages[qid + "/" + prompt] = msg
    checks = read_json(ROOT / "reports/checks.json")
    assert checks["suite_passed"] and checks["skipped_count"] == 0
    write_json(destination, {"status": "PREPARED_IDENTICAL_CONTEXT_AND_MESSAGES",
        "created_at": utc_now(), "runtime_code_id": runtime_code_id(),
        "plan_hash": digest(plan), "script_hash": digest(Path(__file__).read_bytes()),
        "config": cfg, "prepared_contexts": contexts, "messages": messages,
        "checks_hash": digest(checks), "test_count": checks["test_count"],
        "fresh_retrieval_queries": 0, "model_calls": 0})
    print({"prepared": len(messages), "model_calls": 0}, flush=True)


def run():
    plan = read_json(PLAN)
    prepared = read_json(DIRECTORY / "preparation.json")
    assert prepared["plan_hash"] == digest(plan)
    assert prepared["script_hash"] == digest(Path(__file__).read_bytes())
    assert prepared["runtime_code_id"] == runtime_code_id()
    assert prepared["checks_hash"] == digest(read_json(ROOT / "reports/checks.json"))
    assert plan["active_config_id"] == digest(load_config())
    assert plan["corpus_id"] == digest(read_documents())
    assert plan["question_bank_hash"] == digest(read_json(ROOT / "data/evaluation/questions-v2.json"))
    destination = DIRECTORY / "execution.json"
    if destination.exists():
        raise FileExistsError("Inspect execution and actual live handle; do not repeat the run")
    cfg = prepared["config"]
    preflight = inspect_runtime(cfg)
    write_json(DIRECTORY / "preflight.json", preflight)
    assert preflight["status"] == "RUNTIME_METADATA_READY"
    assert preflight["selected_model"]["digest"] == plan["model"]["digest"]
    execution = {"status": "RUNNING", "created_at": utc_now(),
        "preparation_hash": digest(prepared), "planned_calls": 6,
        "official_points": None, "runtime_promoted": False}
    write_json(destination, execution)
    try:
        result = answer_evaluation(config=cfg, question_ids=plan["question_ids"],
            prompt_names=plan["prompts"], prepared_contexts=prepared["prepared_contexts"])
        execution.update(status=result["status"], result_path=result["run_directory"] + "/results.json",
                         result_hash=digest(result), actual_provider_requests=result["actual_provider_requests"])
        write_json(destination, execution)
        for row in result["per_question"]:
            for call in row["record"]["calls"]:
                assert call["messages"] == prepared["messages"][row["question_id"] + "/" + row["prompt"]]
                assert call["generation_json_schema"] is True
                assert call["response_format"]["type"] == "json_schema"
                assert call["provider"] == "ollama" and call["execution_kind"] == "live_provider_client"
                assert call["model_digest"] == plan["model"]["digest"]
        if result["status"] == "EXECUTED_AWAITING_REVIEW":
            assert result["actual_provider_requests"] == 6
        write_json(DIRECTORY / "postflight.json", inspect_runtime(cfg))
    except BaseException as exc:
        execution.update(status="STOPPED_ERROR", error_type=type(exc).__name__)
        raise
    finally:
        execution["completed_at"] = utc_now()
        write_json(destination, execution)
        print(execution, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["prepare", "run"])
    args = parser.parse_args()
    (prepare if args.action == "prepare" else run)()
