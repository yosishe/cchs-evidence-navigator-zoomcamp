"""Iteration 023: replay saved ranks only; no indexing or inference.

Project diagnostic adapted from 2026 evaluation homework Q6. The runtime RRF
function supplies ranking; frozen references supply the previously defined
metrics. A replay cannot select or modify the application's active configuration.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from navigator.common import (
    ROOT, digest, load_config, read_documents, read_json, runtime_code_id,
    utc_now, write_json,
)
from navigator.evaluation import metrics
from navigator.retrieval import reciprocal_rank_fusion


def aggregate(rows):
    eligible = [row for row in rows if row["answerable"]]
    denominator = len(eligible)
    hits = sum(row["metrics"]["hit"] for row in eligible)
    return {
        "questions": len(rows), "answerable_denominator": denominator,
        "hits": hits,
        "hit_at_5": hits / denominator if denominator else None,
        "mrr_at_5": sum(row["metrics"]["reciprocal_rank"] for row in eligible) / denominator if denominator else None,
        "reference_coverage": sum(row["reference_coverage"] for row in eligible) / denominator if denominator else None,
        "fully_covered": sum(row["reference_coverage"] == 1 for row in eligible),
    }


def measure(question, ranked_ids):
    matches = [bool(set(ref["acceptable_ids"]) & set(ranked_ids))
               for ref in question["reference_quotes"]]
    return {
        "reference_matches": matches,
        "reference_coverage": sum(matches) / len(matches) if matches else None,
        "metrics": metrics(ranked_ids, question["relevant_ids"]) if question["answerable"] else None,
    }


def main():
    started = utc_now()
    plan = read_json(ROOT / "reports/goal-loop/iterations/023-rrf-rank-replay.json")
    source = read_json(ROOT / plan["source_artifact"])
    bank = read_json(ROOT / "data/evaluation/questions-v2.json")
    assert digest(source) == plan["source_hash"]
    assert digest(bank) == plan["question_bank_hash"]
    assert runtime_code_id() == plan["runtime_code_id"]
    assert digest(load_config()) == plan["config_id"]
    assert digest(read_documents()) == plan["corpus_id"]
    questions = [q for q in bank["questions"] if q["split"] == plan["split"]]
    assert len(questions) == plan["question_count"] == 42
    assert sum(q["answerable"] for q in questions) == plan["answerable_denominator"] == 35
    expected_ids = [q["id"] for q in questions]
    assert len(expected_ids) == len(set(expected_ids))
    variants = {variant["id"]: variant for variant in source["results"]}
    baseline = variants[plan["source_variant"]]
    incumbent = variants[plan["incumbent_variant"]]
    assert baseline["config"]["boosts"]["title"] == 0
    assert baseline["config"]["rrf_k"] == 50
    for variant in (baseline, incumbent):
        assert [row["id"] for row in variant["per_question"]] == expected_ids
        for q, row in zip(questions, variant["per_question"]):
            assert row["slice"] == q["slice"] and row["answerable"] == q["answerable"]
            for name, value in measure(q, row["ranked_ids"]).items():
                assert row[name] == value, (variant["id"], q["id"], name)
        assert aggregate(variant["per_question"]) == variant["aggregate"]

    branches = {}
    for q, row in zip(questions, baseline["per_question"]):
        trace = row["trace"]
        assert trace["query"] == q["question"] and trace["filters"] == {}
        assert trace["candidate_k"] == plan["candidate_pool"] == 20
        assert trace["final_k"] == plan["top_k"] == 5
        lists = [trace[name] for name in ("lexical", "vector")]
        for ranking in lists:
            assert len(ranking) <= 20
            assert [hit["rank0"] for hit in ranking] == list(range(len(ranking)))
            assert len({hit["id"] for hit in ranking}) == len(ranking)
        # k=50 reconstruction is a prerequisite, not a favorable candidate run.
        reconstructed = reciprocal_rank_fusion(lists, 50)
        assert [hit["id"] for hit in reconstructed[:5]] == row["ranked_ids"]
        assert [{"id": hit["id"], "rank": i, "score": hit["score"]}
                for i, hit in enumerate(reconstructed, 1)] == trace["ranked"]
        branches[q["id"]] = lists

    results = []
    for k in plan["rrf_k_values"]:
        rows = []
        for q, old in zip(questions, incumbent["per_question"]):
            lists = branches[q["id"]]
            ranks = [{hit["id"]: hit["rank0"] for hit in ranking} for ranking in lists]
            fused = reciprocal_rank_fusion(lists, k)
            full = []
            for rank1, hit in enumerate(fused, 1):
                contributions = [1 / (k + branch[hit["id"]]) if hit["id"] in branch else 0.0 for branch in ranks]
                assert hit["score"] == sum(contributions)
                full.append({
                    "id": hit["id"], "rank": rank1, "score": hit["score"],
                    "lexical_rank0": ranks[0].get(hit["id"]),
                    "vector_rank0": ranks[1].get(hit["id"]),
                    "lexical_contribution": contributions[0],
                    "vector_contribution": contributions[1],
                })
            top = [hit["id"] for hit in fused[:5]]
            values = measure(q, top)
            refs = []
            for i, ref in enumerate(q["reference_quotes"]):
                refs.append({
                    "reference_index": i,
                    "acceptable_ids": ref["acceptable_ids"],
                    "incumbent_matched": old["reference_matches"][i],
                    "candidate_matched": values["reference_matches"][i],
                    "candidate_ranks": [{"id": row["id"], "rank": row["rank"]}
                                        for row in full if row["id"] in ref["acceptable_ids"]],
                })
            rows.append({
                "id": q["id"], "slice": q["slice"], "answerable": q["answerable"],
                "ranked_ids": top, **values,
                "incumbent_ranked_ids": old["ranked_ids"],
                "incumbent_reference_coverage": old["reference_coverage"],
                "reference_coverage_delta": values["reference_coverage"] - old["reference_coverage"] if q["answerable"] else None,
                "reference_positions": refs, "full_ranked_contributions": full,
            })
        summary = aggregate(rows)
        gains = [row["id"] for row in rows if row["answerable"] and row["reference_coverage_delta"] > 0]
        losses = [row["id"] for row in rows if row["answerable"] and row["reference_coverage_delta"] < 0]
        nominated = summary["reference_coverage"] > incumbent["aggregate"]["reference_coverage"] and not losses
        results.append({
            "rrf_k": k, "aggregate": summary,
            "slices": {name: aggregate([row for row in rows if row["slice"] == name])
                       for name in sorted({row["slice"] for row in rows})},
            "gains_vs_vector": gains, "losses_vs_vector": losses,
            "qualifies_for_fresh_retrieval_check": nominated,
            "per_question": rows,
        })
    assert len(results) * len(questions) == plan["planned_rank_replays"] == 168
    result = {
        "iteration_id": "023", "status": "EXECUTED_AWAITING_ANALYSIS",
        "started_at": started, "completed_at": utc_now(),
        "predeclared_plan": plan, "predeclared_plan_hash": digest(plan),
        "script_hash": digest(Path(__file__).read_bytes()),
        "baseline_reconstruction": {"questions": 42, "top5_exact": True,
                                    "full_fusion_scores_and_order_exact": True,
                                    "reference_metrics_exact": True},
        "actual_rank_replays": 168, "actual_retrieval_queries": 0,
        "actual_encoder_calls": 0, "actual_model_calls": 0,
        "incumbent": {"id": incumbent["id"], "aggregate": incumbent["aggregate"], "slices": incumbent["slices"]},
        "results": results, "runtime_promoted": False, "official_points": None,
        "limitations": "Saved-rank replay on tuning questions with provisional reference labels. No fresh retrieval, generated-answer, abstention, latency or end-to-end validation. Final-set questions are excluded from computation, not claimed unseen.",
    }
    destination = ROOT / "reports/goal-loop/rrf-rank-replay-023.json"
    if destination.exists():
        raise FileExistsError("Preserve the completed evidence; do not overwrite or rerun it")
    write_json(destination, result)
    for row in results:
        print({key: row[key] for key in ["rrf_k", "aggregate", "gains_vs_vector", "losses_vs_vector", "qualifies_for_fresh_retrieval_check"]})


if __name__ == "__main__":
    main()
