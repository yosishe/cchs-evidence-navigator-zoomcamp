"""Iteration 025: actual offline retrieval for predeclared cutoff candidates."""
from pathlib import Path
import copy
import os
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from navigator.common import (
    ROOT, digest, load_config, read_documents, read_json, runtime_code_id,
    utc_now, write_json,
)
from navigator.evaluation import metrics
from navigator.rag import build_context, prepare_context
from navigator.retrieval import Retriever


def main():
    plan = read_json(ROOT / "reports/goal-loop/iterations/025-fresh-cutoff-retrieval.json")
    directory = ROOT / plan["output_directory"]
    destination = directory / "results.json"
    if destination.exists():
        raise FileExistsError("Inspect the existing terminal/live state; do not rerun or overwrite")
    expected = read_json(ROOT / plan["expected_result_path"])
    bank = read_json(ROOT / "data/evaluation/questions-v2.json")
    config, documents = load_config(), read_documents()
    assert digest(expected) == plan["expected_result_hash"]
    assert digest(bank) == plan["question_bank_hash"]
    assert digest(config) == plan["config_id"]
    assert digest(documents) == plan["corpus_id"]
    assert runtime_code_id() == plan["runtime_code_id"]
    questions = [q for q in bank["questions"] if q["split"] == plan["split"]]
    assert len(questions) == 42 and sum(q["answerable"] for q in questions) == 35
    started = time.perf_counter()
    result = {
        "iteration_id": "025", "status": "RUNNING", "started_at": utc_now(),
        "predeclared_plan": plan, "predeclared_plan_hash": digest(plan),
        "script_hash": digest(Path(__file__).read_bytes()), "pid_at_start": os.getpid(),
        "actual_retrieval_attempts": 0, "completed_retrieval_queries": 0,
        "actual_model_calls": 0, "downloads_allowed": False,
        "candidates": [], "runtime_promoted": False, "official_points": None,
    }
    write_json(destination, result)
    try:
        for candidate in plan["candidates"]:
            name, cutoff = candidate["method"], candidate["cutoff"]
            cfg = copy.deepcopy(config)
            cfg["top_k"] = cutoff
            if name == "hybrid_title_0_rrf_1":
                cfg["retrieval"], cfg["rrf_k"], cfg["boosts"]["title"] = "hybrid", 1, 0.0
            else:
                assert name == "vector"
                cfg["retrieval"] = "vector"
            # Isolate this experiment's encoder metadata from the running app.
            os.environ["NAVIGATOR_RUNTIME"] = str(directory / name)
            target = next(v for v in expected["results"] if v["method"] == name and v["cutoff"] == cutoff)
            rows = {r["id"]: r for r in target["per_question"]}
            current = {"id": name, "cutoff": cutoff, "config": cfg, "per_question": [], "status": "STARTED"}
            result["candidates"].append(current)
            setup = time.perf_counter()
            engine = Retriever(documents, cfg)
            current["lexical_setup_seconds"] = time.perf_counter() - setup
            setup = time.perf_counter()
            engine.load_vectors(allow_download=False)
            current["encoder_and_vector_setup_seconds"] = time.perf_counter() - setup
            embedding = read_json(directory / name / "embedding-report.json")
            current["embedding"] = embedding
            assert embedding["corpus_id"] == plan["corpus_id"]
            assert embedding["resolved_revision"] == config["embedding_revision"]
            assert embedding["truncated_input_count"] == 0
            assert embedding["allow_download"] is False
            assert embedding["input_count"] == len(documents)
            for q in questions:
                result["actual_retrieval_attempts"] += 1
                query_started = time.perf_counter()
                prepared = prepare_context(q["question"], engine, cfg, use_llm=False)
                query_seconds = time.perf_counter() - query_started
                assert prepared["rewrite"]["calls"] == []
                hits = prepared["hits"]
                context = build_context(hits)
                ids = [hit["id"] for hit in hits]
                matches = [bool(set(ref["acceptable_ids"]) & set(ids)) for ref in q["reference_quotes"]]
                score = metrics(ids, q["relevant_ids"]) if q["answerable"] else None
                row = {
                    "id": q["id"], "slice": q["slice"], "answerable": q["answerable"],
                    "ranked_ids": ids, "reference_matches": matches,
                    "reference_coverage": sum(matches) / len(matches) if matches else None,
                    "metrics": score, "query_seconds": query_seconds,
                    "retrieval_seconds": prepared["retrieval_seconds"],
                    "content_characters": sum(len(hit["content"]) for hit in hits),
                    "serialized_context_characters": len(context), "context": context,
                    "context_hash": digest(context), "trace": prepared["retrieval_trace"],
                    "matches_replay": False,
                }
                current["per_question"].append(row)
                result["completed_retrieval_queries"] += 1
                write_json(destination, result)
                for key in ["ranked_ids", "reference_matches", "reference_coverage", "metrics", "content_characters"]:
                    assert row[key] == rows[q["id"]][key], (name, q["id"], key)
                row["matches_replay"] = True
            current["aggregate"] = target["aggregate"]
            current["slices"] = target["slices"]
            current["query_seconds_total"] = sum(row["query_seconds"] for row in current["per_question"])
            current["serialized_context_characters"] = {
                "mean": sum(row["serialized_context_characters"] for row in current["per_question"]) / len(questions),
                "max": max(row["serialized_context_characters"] for row in current["per_question"]),
            }
            current["status"] = "COMPLETE_MATCHES_REPLAY"
            write_json(destination, result)
            print({k: current[k] for k in ["id", "status", "query_seconds_total", "serialized_context_characters"]}, flush=True)
        assert result["actual_retrieval_attempts"] == result["completed_retrieval_queries"] == 84
        result["status"] = "COMPLETE_AWAITING_ANALYSIS"
    except BaseException as exc:
        result["status"] = "STOPPED_FAILED"
        result["error_type"] = type(exc).__name__
        raise
    finally:
        result["completed_at"] = utc_now()
        result["process_seconds"] = time.perf_counter() - started
        result["context_fit_proven"] = False
        result["limitations"] = "Fresh offline retrieval only. No generation, rewrite, model-token capacity, semantic precision, scientific validation, browser or Compose proof. Sequential warm-cache timings are descriptive, not a controlled speed comparison. Final questions excluded from execution, not claimed unseen."
        write_json(destination, result)


if __name__ == "__main__":
    main()
