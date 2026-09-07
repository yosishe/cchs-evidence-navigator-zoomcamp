"""Iteration 026: staged, predeclared retrieval-only answer experiment.

--prepare makes eight offline context queries. --run invokes exactly the existing
application evaluator, with no paid fallback, prompt changes or automatic retry.
"""
from pathlib import Path
import argparse
import copy
import os
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from navigator.common import ROOT, digest, load_config, read_documents, read_json, runtime_code_id, utc_now, write_json
from navigator.evaluation import answer_evaluation
from navigator.preflight import inspect_runtime
from navigator.rag import OUTPUT_RULES, PROMPTS, build_context, generation_messages, prepare_context
from navigator.retrieval import Retriever

DIRECTORY = ROOT / "reports/goal-loop/cutoff-answer-026"
PLAN = ROOT / "reports/goal-loop/iterations/026-cutoff-answer-pilot.json"


def inputs():
    plan = read_json(PLAN)
    assert runtime_code_id() == plan["runtime_code_id"]
    assert digest(load_config()) == plan["active_config_id"]
    assert digest(read_documents()) == plan["corpus_id"]
    bank = read_json(ROOT / "data/evaluation/questions-v2.json")
    assert digest(bank) == plan["question_bank_hash"]
    assert digest(read_json(ROOT / plan["baseline_path"])) == plan["baseline_hash"]
    questions = {q["id"]: q for q in bank["questions"] if q["split"] == "tuning"}
    return plan, {key: questions[key] for key in plan["question_ids"]}


def prepare():
    plan, questions = inputs()
    destination = DIRECTORY / "contexts.json"
    if destination.exists():
        raise FileExistsError("Do not repeat completed preparation")
    previous = read_json(ROOT / plan["fresh_retrieval_path"])
    assert digest(previous) == plan["fresh_retrieval_hash"]
    documents = read_documents()
    report = {"status": "PREPARING", "created_at": utc_now(),
              "predeclared_plan": plan, "predeclared_plan_hash": digest(plan),
              "script_hash": digest(Path(__file__).read_bytes()),
              "retrieval_attempts": 0, "completed_retrieval_queries": 0,
              "model_calls": 0, "candidates": []}
    write_json(destination, report)
    try:
        for candidate in plan["candidates"]:
            cfg, name = candidate["config"], candidate["id"]
            target_name = "vector" if name == "vector_10" else "hybrid_title_0_rrf_1"
            target = next(c for c in previous["candidates"] if c["id"] == target_name)
            expected = {row["id"]: row for row in target["per_question"]}
            engine = Retriever(documents, cfg)
            original_runtime = os.environ.get("NAVIGATOR_RUNTIME")
            try:
                os.environ["NAVIGATOR_RUNTIME"] = str(DIRECTORY / name)
                engine.load_vectors(allow_download=False)
            finally:
                if original_runtime is None:
                    os.environ.pop("NAVIGATOR_RUNTIME", None)
                else:
                    os.environ["NAVIGATOR_RUNTIME"] = original_runtime
            current = {"id": name, "config": cfg, "prepared_contexts": {}, "expected_messages": {}}
            report["candidates"].append(current)
            for key, q in questions.items():
                report["retrieval_attempts"] += 1
                prepared = prepare_context(q["question"], engine, cfg, filters=q.get("filters", {}), use_llm=False)
                report["completed_retrieval_queries"] += 1
                context = build_context(prepared["hits"])
                current["prepared_contexts"][key] = prepared
                write_json(destination, report)
                assert context == expected[key]["context"]
                assert [hit["id"] for hit in prepared["hits"]] == expected[key]["ranked_ids"]
                assert prepared["rewrite"]["calls"] == []
                current["expected_messages"][key] = generation_messages(
                    q["question"], context, PROMPTS["evidence_first"] + "\n" + OUTPUT_RULES, cfg)
            current["prepared_contexts_hash"] = digest(current["prepared_contexts"])
        assert report["retrieval_attempts"] == report["completed_retrieval_queries"] == 8
        report["status"] = "PREPARED_EXACT_CONTEXT_MATCH"
    except BaseException as exc:
        report.update(status="STOPPED_PREPARATION_ERROR", error_type=type(exc).__name__)
        raise
    finally:
        report["completed_at"] = utc_now()
        write_json(destination, report)
    print({k: report[k] for k in ["status", "retrieval_attempts", "model_calls"]}, flush=True)


def run():
    plan, questions = inputs()
    context_report = read_json(DIRECTORY / "contexts.json")
    assert context_report["status"] == "PREPARED_EXACT_CONTEXT_MATCH"
    assert context_report["predeclared_plan_hash"] == digest(plan)
    assert context_report["script_hash"] == digest(Path(__file__).read_bytes())
    destination = DIRECTORY / "execution.json"
    if destination.exists():
        raise FileExistsError("Inspect the existing execution and process handle; do not restart")
    execution = {"status": "RUNNING", "created_at": utc_now(),
                 "plan_hash": digest(plan), "context_report_hash": digest(context_report),
                 "model_calls": 0, "runs": [], "runtime_promoted": False, "official_points": None}
    write_json(destination, execution)
    try:
        for candidate in context_report["candidates"]:
            assert digest(candidate["prepared_contexts"]) == candidate["prepared_contexts_hash"]
            cfg = copy.deepcopy(candidate["config"])
            cfg["model_digest"] = plan["model"]["digest"]
            execution["active_candidate"] = candidate["id"]
            write_json(destination, execution)
            print({"starting_candidate": candidate["id"], "planned_calls": 4}, flush=True)
            result = answer_evaluation(config=cfg, question_ids=plan["question_ids"],
                prompt_names=plan["prompts"], prepared_contexts=candidate["prepared_contexts"])
            run_record = {"id": candidate["id"], "path": result["run_directory"],
                          "status": result["status"], "result_hash": digest(result),
                          "model_calls": result["actual_provider_requests"]}
            execution["runs"].append(run_record)
            execution["model_calls"] += result["actual_provider_requests"]
            write_json(destination, execution)
            for row in result["per_question"]:
                assert row["prompt"] == "evidence_first"
                for call in row["record"]["calls"]:
                    assert call["execution_kind"] == "live_provider_client"
                    assert call["provider"] == "ollama" and call["model_digest"] == plan["model"]["digest"]
                    assert call["messages"] == candidate["expected_messages"][row["question_id"]]
            postflight = inspect_runtime(cfg)
            write_json(DIRECTORY / (candidate["id"] + "-postflight.json"), postflight)
            run_record["postflight_status"] = postflight["status"]
            run_record["loaded_context_tokens_after_arm"] = postflight.get("loaded_context_tokens")
            print(run_record, flush=True)
            if result["status"] != "EXECUTED_AWAITING_REVIEW":
                execution["status"] = "STOPPED_ARM_FAILURE"
                break
        else:
            assert execution["model_calls"] == plan["planned_model_calls"] == 8
            execution["status"] = "COMPLETED_AWAITING_REVIEW"
    except BaseException as exc:
        execution.update(status="STOPPED_ERROR", error_type=type(exc).__name__)
        raise
    finally:
        execution["completed_at"] = utc_now()
        write_json(destination, execution)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare", action="store_true")
    group.add_argument("--run", action="store_true")
    args = parser.parse_args()
    prepare() if args.prepare else run()
