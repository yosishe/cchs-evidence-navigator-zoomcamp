"""Module 4 Hit/MRR and controlled prompt comparisons; original evidence reports."""
from __future__ import annotations

import copy
import time
import uuid

from .common import ROOT, digest, load_config, read_documents, read_json, utc_now, write_json, runtime_code_id, verify_generation_selection
from .rag import PROMPTS, prepare_context, run_request
from .retrieval import Retriever


def load_question_bank(cfg, docs):
    bank = read_json(ROOT / cfg.get("question_bank", "data/evaluation/questions.json"))
    validate_questions(bank["questions"], docs)
    if bank.get("corpus_id") != digest(docs):
        raise ValueError("Question bank belongs to a different corpus version")
    return bank


def metrics(ranked, relevant):
    wanted = set(relevant)
    for rank, hit in enumerate(ranked, 1):
        if hit in wanted:
            return {"hit": 1, "reciprocal_rank": 1 / rank}
    return {"hit": 0, "reciprocal_rank": 0.0}


def validate_questions(questions, documents):
    lookup = {d["id"]: d for d in documents}
    groups = {}
    ids = set()
    for q in questions:
        if q.get("id"):
            if q["id"] in ids:
                raise ValueError("Duplicate question ID")
            ids.add(q["id"])
        group = q["group_id"]
        if group in groups and groups[group] != q["split"]:
            raise ValueError("Question group leaks across tuning and test splits")
        groups[group] = q["split"]
        if q["answerable"] and not q["relevant_ids"]:
            raise ValueError("Answerable question has no gold passages")
        for key in q["relevant_ids"]:
            if key not in lookup:
                raise ValueError("Gold passage does not exist in this corpus version")
        for ref in q.get("reference_quotes", []):
            if (not ref.get("quote", "").strip() or ref["id"] not in lookup
                    or ref["quote"] not in lookup[ref["id"]]["content"]):
                raise ValueError("Reference quote does not match its passage")
        if q.get("schema_version") == 2:
            facts = q.get("required_facts", [])
            if q["answerable"] and (not facts or not q.get("reference_quotes")):
                raise ValueError("Answerable v2 question needs facts and exact reference evidence")
            if not q["answerable"] and (facts or not q.get("abstention_reason", "").strip()):
                raise ValueError("Unanswerable question needs a corpus-scoped abstention reason")
            for fact in facts + q.get("required_qualifications", []):
                if not fact.get("text", "").strip() or not fact.get("reference_indices"):
                    raise ValueError("Expected fact/qualification needs a reference")
                if any(type(i) is not int or i < 0 or i >= len(q["reference_quotes"]) for i in fact["reference_indices"]):
                    raise ValueError("Expected fact points outside its reference evidence")


def retrieval_evaluation(methods, split="tuning", config=None):
    cfg, docs = config or load_config(), read_documents()
    bank = load_question_bank(cfg, docs)
    questions = [q for q in bank["questions"] if q["split"] == split]
    if not questions:
        raise ValueError("No questions in selected split")
    setup_started = time.perf_counter()
    engine = Retriever(docs, cfg)
    lexical_setup_seconds = time.perf_counter() - setup_started
    rows, aggregates = [], []
    for method in methods:
        setup_started = time.perf_counter()
        if method in {"vector", "hybrid"}:
            engine.load_vectors()
        setup_seconds = time.perf_counter() - setup_started
        start = time.perf_counter()
        eligible = []
        for q in questions:
            t = time.perf_counter()
            hits = engine.search(q["question"], method=method)
            score = metrics([h["id"] for h in hits], q["relevant_ids"]) if q["answerable"] else None
            if score:
                eligible.append(score)
            rows.append({"question_id": q["id"], "method": method, "ranked_ids": [h["id"] for h in hits],
                         "seconds": time.perf_counter() - t, "metrics": score,
                         "answerable": q["answerable"], "label_status": q["label_status"]})
        aggregates.append({"method": method, "answerable_denominator": len(eligible),
                           "hit_at_k": sum(x["hit"] for x in eligible) / len(eligible) if eligible else None,
                           "mrr_at_k": sum(x["reciprocal_rank"] for x in eligible) / len(eligible) if eligible else None,
                           "query_seconds_excluding_setup": time.perf_counter() - start,
                           "additional_setup_seconds": setup_seconds})
    report = {"status": "EXECUTED_PROVISIONAL_LABELS", "created_at": utc_now(), "split": split,
              "corpus_id": digest(docs), "questions_hash": digest(bank), "config": cfg,
              "config_id": digest(cfg), "aggregates": aggregates, "per_question": rows,
              "shared_lexical_setup_seconds": lexical_setup_seconds,
              "timing_scope": "Search only; initial index/encoder setup reported separately. Hybrid reuses the vector index if already built.",
              "limitations": "Assistant-authored labels require researcher review. Unanswerable queries are excluded from Hit/MRR and need answer-abstention review. No automatic configuration promotion."}
    write_json(ROOT / "reports" / f"retrieval-{split}.json", report)
    run_id = str(uuid.uuid4())
    write_json(ROOT / "reports/experiments" / f"retrieval-{split}-{run_id}.json", report)
    return report


def answer_plan(split="tuning", max_questions=None, *, config=None, question_ids=None, prompt_names=None):
    """Plan first; stratified development pilots, one selected prompt on test."""
    cfg, docs = config or load_config(), read_documents()
    if split == "test" and (max_questions is not None or question_ids is not None or prompt_names is not None):
        raise ValueError("Final test uses the complete split and selected prompt, without overrides")
    if prompt_names is not None and (not prompt_names or len(set(prompt_names)) != len(prompt_names)
                                    or any(p not in PROMPTS for p in prompt_names)):
        raise ValueError("Use unique implemented prompt names")
    bank = load_question_bank(cfg, docs)
    selected = [q for q in bank["questions"] if q["split"] == split]
    if question_ids is not None:
        lookup = {q["id"]: q for q in selected}
        if (not question_ids or len(set(question_ids)) != len(question_ids)
                or any(key not in lookup for key in question_ids) or max_questions is not None):
            raise ValueError("Use unique question IDs from the requested split, without a cap")
        selected = [lookup[key] for key in question_ids]
    if not selected or (max_questions is not None and max_questions < 1):
        raise ValueError("No questions or invalid question cap")
    if max_questions is not None and max_questions < len(selected):
        answerable = [q for q in selected if q["answerable"]]
        unanswerable = [q for q in selected if not q["answerable"]]
        if answerable and unanswerable:
            if max_questions < 2:
                raise ValueError("At least two questions are needed to cover both answerability strata")
            required = [answerable[0], unanswerable[0]]
            # Cover other slices before taking a second question from a slice.
            covered = {q.get("slice", str(q["answerable"])) for q in required}
            for q in selected:
                key = q.get("slice", str(q["answerable"]))
                if key not in covered:
                    required.append(q)
                    covered.add(key)
            selected = (required + [q for q in selected if q not in required])[:max_questions]
        else:
            selected = selected[:max_questions]
    prompts = [cfg["prompt"]] if split == "test" else list(prompt_names or ["concise", "evidence_first"])
    generation_limit = len(prompts) * len(selected)
    rewrite_limit = len(selected) if cfg.get("rewrite_enabled", False) else 0
    return {"status": "PLANNED_NOT_EXECUTED", "split": split,
            "runtime_code_id": runtime_code_id(),
            "questions": selected, "questions_hash": digest(bank),
            "config": cfg, "config_id": digest(cfg), "corpus_id": digest(docs),
            "prompts": prompts, "covered_slices": sorted({q.get("slice", "unknown") for q in selected}),
            "maximum_generation_requests": generation_limit, "maximum_rewrite_requests": rewrite_limit,
            "maximum_provider_requests": generation_limit + rewrite_limit,
            "maximum_output_tokens": generation_limit * cfg["max_output_tokens"] + rewrite_limit * min(cfg["max_output_tokens"], 256),
            "quality_review": "Per-question relevance, every-claim support and abstention review are required; no quality scores from JSON validity."}


def answer_evaluation(split="tuning", max_questions=None, *, client=None, config=None,
                      question_ids=None, prepared_contexts=None, prompt_names=None):
    from .providers import validate_provider, model_identity
    cfg = copy.deepcopy(config or load_config())
    if split == "test" and (max_questions is not None or question_ids is not None
            or not cfg.get("generation_selection_status", "").startswith("SELECTED")):
        raise ValueError("Final test requires the selected configuration and the complete split")
    if split == "test":
        verify_generation_selection(cfg)
    else:
        cfg["generation_selection_status"] = "EVALUATION_CANDIDATE"
        cfg.pop("generation_selection_artifact", None)
    plan = answer_plan(split, max_questions, config=cfg, question_ids=question_ids, prompt_names=prompt_names)
    cfg, docs = plan["config"], read_documents()
    if digest(docs) != plan["corpus_id"]:
        raise ValueError("Corpus changed after evaluation planning")
    run_dir = ROOT / "reports/experiments" / ("answers-" + str(uuid.uuid4()))
    report = {**plan, "status": "PREFLIGHT", "created_at": utc_now(), "per_question": [],
              "run_directory": str(run_dir.relative_to(ROOT)),
              "judgment_status": "PENDING_REVIEW", "actual_provider_requests": 0,
              "preparation_calls": [], "contexts": {}}
    write_json(run_dir / "results.json", report)
    try:
        validate_provider(cfg)
        if client is None:
            identity = model_identity(cfg)
            cfg["model_digest"] = identity["digest"]
            report.update(model_identity=identity, config=cfg, config_id=digest(cfg))
        engine = Retriever(docs, cfg)
    except Exception as exc:
        report.update(status="BLOCKED_PREFLIGHT", error_type=type(exc).__name__)
        write_json(run_dir / "results.json", report)
        return report
    report["status"] = "RUNNING"
    for q in plan["questions"]:
        try:
            filters = q.get("filters", {})
            prepared = (prepared_contexts[q["id"]] if prepared_contexts is not None else
                        prepare_context(q["question"], engine, cfg, filters=filters, client=client))
            report["contexts"][q["id"]] = copy.deepcopy(prepared)
            if prepared_contexts is None:
                report["preparation_calls"].extend(copy.deepcopy(prepared["rewrite"]["calls"]))
                report["actual_provider_requests"] += len(prepared["rewrite"]["calls"])
            write_json(run_dir / "results.json", report)
        except Exception as exc:
            report.update(status="STOPPED_ON_RETRIEVAL_ERROR", error_type=type(exc).__name__, failed_question=q["id"])
            break
        for prompt in plan["prompts"]:
            variant = copy.deepcopy(cfg)
            variant["prompt"] = prompt
            try:
                if runtime_code_id() != report["runtime_code_id"]:
                    raise ValueError("Runtime code changed during evaluation")
                rec = run_request(q["question"], engine, variant, filters=filters, use_llm=True,
                                  prepared_context=prepared, client=client, traffic_origin="evaluation")
            except Exception as exc:
                report.update(status="STOPPED_ON_ERROR", error_type=type(exc).__name__, failed_question=q["id"])
                write_json(run_dir / "results.json", report)
                break
            report["actual_provider_requests"] += len(rec["calls"])
            report["per_question"].append({"question_id": q["id"], "answerable": q["answerable"],
                "reference_quotes": q.get("reference_quotes", []), "prompt": prompt,
                "record": rec, "record_hash": digest(rec)})
            write_json(run_dir / "results.json", report)
            # A completed but invalid answer is a measured failure, not missing
            # data. Keep it in both prompts' denominator; never retry it. Stop on
            # infrastructure/provider errors rather than exhaust a broken service.
            if rec["status"] == "error" and rec.get("error_stage") != "output_validation":
                report["status"] = "STOPPED_ON_ERROR"
                break
        if report["status"] == "STOPPED_ON_ERROR":
            break
    if report["status"] == "RUNNING":
        report["status"] = "EXECUTED_AWAITING_REVIEW"
    template = {"reviewer": "", "reviewer_kind": "", "results_hash": digest(report), "reviews": [
        {"answer_id": r["record"]["id"], "record_hash": r["record_hash"],
         "relevance": None, "claim_support": [None for _ in r["record"]["claims"]],
         "abstention_correct": None, "fact_coverage": [None] * len(next(q for q in plan["questions"] if q["id"] == r["question_id"]).get("required_facts", [])),
         "qualification_coverage": [None] * len(next(q for q in plan["questions"] if q["id"] == r["question_id"]).get("required_qualifications", [])), "reason": ""}
        for r in report["per_question"]]}
    write_json(run_dir / "results.json", report)
    write_json(run_dir / "review-template.json", template)
    from .whole_review import whole_review_template
    write_json(run_dir / "whole-answer-review-template.json", whole_review_template(report))
    return report


def summarize_answer_review(results, reviews):
    """Original evidence rubric, using the course's paired comparison principle."""
    if reviews.get("results_hash") != digest(results):
        raise ValueError("Review belongs to a different result artifact")
    if not reviews.get("reviewer", "").strip() or reviews.get("reviewer_kind") not in {"human", "assistant", "llm_judge"}:
        raise ValueError("Reviewer identity and kind must be explicit")
    rows = results["per_question"]
    pairs = [(r["question_id"], r["prompt"]) for r in rows]
    expected = {(q["id"], p) for q in results["questions"] for p in results["prompts"]}
    if len(set(pairs)) != len(pairs) or not set(pairs) <= expected:
        raise ValueError("Duplicate or unexpected question/prompt pair")
    if results["status"] == "EXECUTED_AWAITING_REVIEW" and set(pairs) != expected:
        raise ValueError("Completed run is missing question/prompt pairs")
    contexts = {}
    for row in rows:
        rec = row["record"]
        if rec["config"]["prompt"] != row["prompt"]:
            raise ValueError("Prompt label differs from the executed configuration")
        context_id = digest({"question": rec["question"], "corpus_id": rec["corpus_id"], "hits": rec["hits"]})
        if contexts.setdefault(row["question_id"], context_id) != context_id:
            raise ValueError("Prompt comparison used different question/context inputs")
    judgments = {r["answer_id"]: r for r in reviews["reviews"]}
    if len(judgments) != len(reviews["reviews"]) or set(judgments) != {r["record"]["id"] for r in rows}:
        raise ValueError("Missing, duplicate or foreign answer reviews")
    by_prompt = {p: [] for p in results["prompts"]}
    details = []
    questions = {q["id"]: q for q in results["questions"]}
    completeness_available = all("required_facts" in q and "required_qualifications" in q for q in questions.values())
    for row in rows:
        rec = row["record"]; review = judgments[rec["id"]]
        if digest(rec) != row["record_hash"] or review["record_hash"] != row["record_hash"]:
            raise ValueError("Answer content changed after review")
        if review["relevance"] not in {"relevant", "partly_relevant", "not_relevant"}:
            raise ValueError("Every response needs an explicit relevance judgment")
        support = review["claim_support"]
        if len(support) != len(rec["claims"]) or any(v not in {"supported", "partial", "unsupported", "uncertain"} for v in support):
            raise ValueError("Every claim needs a source-support judgment")
        if type(review["abstention_correct"]) is not bool or not review["reason"].strip():
            raise ValueError("Abstention judgment and reason are required")
        q = questions[row["question_id"]]
        if "answerable" in q and q["answerable"] != row["answerable"]:
            raise ValueError("Answerability differs from the frozen question")
        coverage = []
        for field, expected_field in [("fact_coverage", "required_facts"), ("qualification_coverage", "required_qualifications")]:
            if completeness_available:
                labels = review.get(field)
                if (not isinstance(labels, list) or len(labels) != len(q[expected_field])
                        or any(v not in {"covered", "partial", "missing", "uncertain"} for v in labels)):
                    raise ValueError("Every required fact and qualification needs a coverage judgment")
                coverage.extend(labels)
        complete_answer = completeness_available and all(v == "covered" for v in coverage)
        acceptable = (rec["status"] == "answered" and review["relevance"] == "relevant"
                      and bool(support) and all(v == "supported" for v in support) and complete_answer) if row["answerable"] else (
                      rec["status"] == "insufficient_evidence" and not rec["claims"] and review["abstention_correct"])
        by_prompt[row["prompt"]].append({"acceptable": bool(acceptable), "relevance": review["relevance"],
                                        "support": support, "seconds": rec["seconds"], "status": rec["status"],
                                        "slice": q.get("slice", "unknown"), "answerable": row["answerable"]})
        details.append({"question_id": row["question_id"], "answer_id": rec["id"],
                        "prompt": row["prompt"], "slice": q.get("slice", "unknown"),
                        "answerable": row["answerable"], "acceptable": bool(acceptable),
                        "claim_support": support, "fact_coverage": review.get("fact_coverage"),
                        "qualification_coverage": review.get("qualification_coverage"),
                        "abstention_correct": review["abstention_correct"], "reason": review["reason"]})
    aggregates = []
    for prompt, values in by_prompt.items():
        supports = [v for row in values for v in row["support"]]
        aggregates.append({"prompt": prompt, "evaluated_questions": len(values),
            "acceptable_answers": sum(v["acceptable"] for v in values),
            "acceptable_rate": sum(v["acceptable"] for v in values) / len(values) if values else None,
            "supported_claims": supports.count("supported"), "claim_denominator": len(supports),
            "unsupported_claims": supports.count("unsupported"),
            "mean_seconds": sum(v["seconds"] for v in values) / len(values) if values else None,
            "errors": sum(v["status"] == "error" for v in values)})
    slices = []
    for prompt, values in by_prompt.items():
        for slice_name in sorted({v["slice"] for v in values}):
            group = [v for v in values if v["slice"] == slice_name]
            slices.append({"prompt": prompt, "slice": slice_name,
                           "evaluated_questions": len(group),
                           "acceptable_answers": sum(v["acceptable"] for v in group),
                           "acceptable_rate": sum(v["acceptable"] for v in group) / len(group)})
    complete = (completeness_available and results["status"] == "EXECUTED_AWAITING_REVIEW" and all(
        a["evaluated_questions"] == len(results["questions"]) for a in aggregates))
    best = max(a["acceptable_rate"] or 0 for a in aggregates)
    return {"status": "REVIEWED_COMPLETE" if complete else "REVIEWED_INCOMPLETE_NO_SELECTION",
        "results_hash": digest(results), "reviews_hash": digest(reviews),
        "reviewer": reviews["reviewer"], "reviewer_kind": reviews["reviewer_kind"],
        "aggregates": aggregates, "per_slice": slices, "per_question": details,
        "eligible_best_prompts": [a["prompt"] for a in aggregates if a["acceptable_rate"] == best] if complete and best > 0 and results.get("split", "tuning") == "tuning" else [],
        "completeness_available": completeness_available,
        "completion_note": "Complete means every planned pair was run and reviewed, not that every answer succeeded. Invalid outputs count as unacceptable answers and errors.",
        "selection_rule": "Highest supported, complete and relevant response rate on tuning data. Zero-quality, legacy incomplete-reference and test-only results cannot nominate a winner. No automatic promotion.",
        "limitations": "Reviewer judgments are not a clinical validation. Assistant or model review must never be labeled human review."}
