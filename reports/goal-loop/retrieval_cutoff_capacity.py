"""Iteration 024: saved-rank cutoff/coverage diagnostic, never runtime selection."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from navigator.common import (
    ROOT, digest, load_config, read_documents, read_json, runtime_code_id,
    utc_now, write_json,
)
from navigator.evaluation import metrics


def summarize(rows):
    answerable = [r for r in rows if r["answerable"]]
    n = len(answerable)
    return {
        "questions": len(rows), "answerable_denominator": n,
        "hits": sum(r["metrics"]["hit"] for r in answerable),
        "hit_at_cutoff": sum(r["metrics"]["hit"] for r in answerable) / n if n else None,
        "mrr_at_cutoff": sum(r["metrics"]["reciprocal_rank"] for r in answerable) / n if n else None,
        "mean_reference_coverage": sum(r["reference_coverage"] for r in answerable) / n if n else None,
        "fully_covered": sum(r["reference_coverage"] == 1 for r in answerable),
        "mean_content_characters": sum(r["content_characters"] for r in rows) / len(rows),
        "max_content_characters": max(r["content_characters"] for r in rows),
    }


def main():
    started = utc_now()
    destination = ROOT / "reports/goal-loop/retrieval-cutoff-capacity-024.json"
    if destination.exists():
        raise FileExistsError("Preserve completed evidence; no overwrite")
    plan = read_json(ROOT / "reports/goal-loop/iterations/024-retrieval-cutoff-capacity.json")
    source = read_json(ROOT / plan["source_artifact"])
    rrf = read_json(ROOT / plan["rrf_artifact"])
    bank = read_json(ROOT / "data/evaluation/questions-v2.json")
    documents = read_documents()
    assert digest(source) == plan["source_hash"]
    assert digest(rrf) == plan["rrf_artifact_hash"]
    assert digest(bank) == plan["question_bank_hash"]
    assert digest(documents) == plan["corpus_id"]
    assert digest(load_config()) == plan["config_id"]
    assert runtime_code_id() == plan["runtime_code_id"]
    docs = {d["id"]: d for d in documents}
    questions = [q for q in bank["questions"] if q["split"] == plan["split"]]
    assert len(questions) == 42 and sum(q["answerable"] for q in questions) == 35
    ids = [q["id"] for q in questions]
    assert len(set(ids)) == len(ids)
    baseline = next(v for v in source["results"] if v["id"] == "vector_incumbent")
    branch_source = next(v for v in source["results"] if v["id"] == "hybrid_title_0.0")
    fusion = next(v for v in rrf["results"] if v["rrf_k"] == 1)
    for item in (baseline, branch_source, fusion):
        assert [r["id"] for r in item["per_question"]] == ids
    rankings = {method: {} for method in plan["candidate_methods"]}
    branches = {}
    old = {r["id"]: r for r in baseline["per_question"]}
    for q, branch, combined, incumbent in zip(questions, branch_source["per_question"], fusion["per_question"], baseline["per_question"]):
        vector = [h["id"] for h in branch["trace"]["vector"]]
        lexical = [h["id"] for h in branch["trace"]["lexical"]]
        full_fusion = [h["id"] for h in combined["full_ranked_contributions"]]
        assert vector[:5] == incumbent["ranked_ids"]
        assert full_fusion[:5] == combined["ranked_ids"]
        assert len(vector) == len(set(vector)) <= plan["candidate_pool"]
        assert len(full_fusion) == len(set(full_fusion))
        assert set(full_fusion) == set(vector) | set(lexical)
        rankings["vector"][q["id"]] = vector
        rankings["hybrid_title_0_rrf_1"][q["id"]] = full_fusion
        branches[q["id"]] = {"vector": vector, "lexical": lexical}

    results = []
    for method in plan["candidate_methods"]:
        for cutoff in plan["cutoffs"]:
            rows = []
            for q in questions:
                full = rankings[method][q["id"]]
                selected = full[:cutoff]
                matched = [bool(set(ref["acceptable_ids"]) & set(selected)) for ref in q["reference_quotes"]]
                coverage = sum(matched) / len(matched) if matched else None
                score = metrics(selected, q["relevant_ids"]) if q["answerable"] else None
                if cutoff == 5:
                    expected = old[q["id"]] if method == "vector" else next(r for r in fusion["per_question"] if r["id"] == q["id"])
                    assert selected == expected["ranked_ids"]
                    assert matched == expected["reference_matches"]
                    assert coverage == expected["reference_coverage"]
                    assert score == expected["metrics"]
                refs = []
                for i, ref in enumerate(q["reference_quotes"]):
                    accepted = set(ref["acceptable_ids"])
                    assert accepted <= set(docs)
                    assert ref["quote"] in docs[ref["id"]]["content"]
                    positions = [n for n, key in enumerate(full, 1) if key in accepted]
                    refs.append({
                        "reference_index": i, "acceptable_ids": ref["acceptable_ids"],
                        "matched": matched[i], "best_method_rank": min(positions) if positions else None,
                        "vector_ranks": [n for n, key in enumerate(branches[q["id"]]["vector"], 1) if key in accepted],
                        "lexical_ranks": [n for n, key in enumerate(branches[q["id"]]["lexical"], 1) if key in accepted],
                        "classification": "RETRIEVED" if matched[i] else ("RANK_BELOW_FINAL_CUTOFF" if positions else "REFERENCE_ABSENT_FROM_METHOD_CANDIDATE_LIST"),
                    })
                rows.append({
                    "id": q["id"], "slice": q["slice"], "answerable": q["answerable"],
                    "ranked_ids": selected, "returned_count": len(selected),
                    "content_characters": sum(len(docs[key]["content"]) for key in selected),
                    "metrics": score, "reference_matches": matched, "reference_coverage": coverage,
                    "delta_vs_vector_at_5": coverage - old[q["id"]]["reference_coverage"] if q["answerable"] else None,
                    "references": refs,
                })
            summary = summarize(rows)
            gains = [r["id"] for r in rows if r["answerable"] and r["delta_vs_vector_at_5"] > 0]
            losses = [r["id"] for r in rows if r["answerable"] and r["delta_vs_vector_at_5"] < 0]
            eligible = summary["fully_covered"] > baseline["aggregate"]["fully_covered"] and not losses
            results.append({
                "method": method, "cutoff": cutoff, "aggregate": summary,
                "slices": {name: summarize([r for r in rows if r["slice"] == name]) for name in sorted({r["slice"] for r in rows})},
                "gains_vs_vector_at_5": gains, "losses_vs_vector_at_5": losses,
                "eligible_for_runtime_capacity_check": eligible, "per_question": rows,
            })
    next_checks = []
    for method in plan["candidate_methods"]:
        eligible = [r for r in results if r["method"] == method and r["eligible_for_runtime_capacity_check"]]
        if eligible:
            smallest = min(eligible, key=lambda r: r["cutoff"])
            next_checks.append({"method": method, "cutoff": smallest["cutoff"]})
    result = {
        "iteration_id": "024", "status": "EXECUTED_AWAITING_ANALYSIS", "started_at": started, "completed_at": utc_now(),
        "predeclared_plan": plan, "predeclared_plan_hash": digest(plan), "script_hash": digest(Path(__file__).read_bytes()),
        "baseline_reconstruction": {"vector_at_5_questions": 42, "rrf1_at_5_questions": 42, "ids_and_metrics_exact": True},
        "actual_rank_replays": len(results) * len(questions), "actual_retrieval_queries": 0, "actual_encoder_calls": 0, "actual_model_calls": 0,
        "results": results, "next_runtime_capacity_checks": next_checks,
        "runtime_promoted": False, "official_points": None,
        "limitations": "Reference-entry coverage on a small provisionally labeled development bank, not semantic precision or answer quality. Content characters exclude metadata, instructions, chat template and output budget and are not model tokens. No context-fit, speed, model, browser, final or Compose proof.",
    }
    assert result["actual_rank_replays"] == plan["planned_rank_replays"] == 252
    write_json(destination, result)
    for r in results:
        print({k: r[k] for k in ["method", "cutoff", "aggregate", "losses_vs_vector_at_5", "eligible_for_runtime_capacity_check"]})
    print({"next_runtime_capacity_checks": next_checks})


if __name__ == "__main__":
    main()
