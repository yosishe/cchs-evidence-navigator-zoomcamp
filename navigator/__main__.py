import argparse
import json
from pathlib import Path

from .common import ROOT, load_config, read_documents, read_json, write_json


def emit_report(report, keys=None):
    """CLI completion is not a quality claim; blocked/partial work exits nonzero."""
    print(json.dumps({k: report[k] for k in keys} if keys else report, indent=2))
    status = report.get("status", "UNKNOWN")
    completed = {"EXECUTED", "PLANNED_NOT_EXECUTED", "EXECUTED_PROVISIONAL_LABELS",
                 "EXECUTED_AWAITING_REVIEW", "EXECUTED_AWAITING_SELECTION",
                 "EXECUTED_AWAITING_COMPARISON", "EXECUTED_AWAITING_INTENT_REVIEW",
                 "REVIEWED_COMPLETE", "PASS_FIXTURES_ONLY", "SELECTION_PREVIEW_NOT_APPLIED",
                 "SELECTED_ON_PROVISIONAL_AGENT_REVIEW", "ENCODER_READY", "RUNTIME_METADATA_READY"}
    if status not in completed:
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description="CCHS evidence corpus and evaluation tools")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("ingest")
    preflight = sub.add_parser("check-runtime", help="Read local versions/model metadata; never download or generate")
    preflight.add_argument("--output", type=Path)
    encoder = sub.add_parser("prepare-encoder", help="Check pinned encoder/cache offline; no LLM calls")
    encoder.add_argument("--allow-download", action="store_true", help="Allow encoder download only after owner approval")
    matrix = sub.add_parser("evaluate-local-matrix", help="Two course models and two prompts; no download or paid fallback")
    matrix.add_argument("--max-questions", type=int)
    matrix.add_argument("--no-judge", action="store_true")
    matrix.add_argument("--calibration", type=Path)
    matrix.add_argument("--question-ids", nargs="+")
    rewrite = sub.add_parser("evaluate-rewrite", help="Tuning-only local rewrite comparison")
    rewrite.add_argument("--max-questions", type=int)
    sub.add_parser("calibrate-judge", help="Five explicitly fictional known-error fixtures")
    diagnostic = sub.add_parser("diagnose-answers", help="Rerun failures with known reference context")
    diagnostic.add_argument("results", type=Path)
    diagnostic.add_argument("--reviews", type=Path)
    search = sub.add_parser("search")
    search.add_argument("question")
    ev = sub.add_parser("evaluate-retrieval")
    ev.add_argument("--methods", nargs="+", choices=["lexical", "vector", "hybrid"], default=["lexical"])
    ev.add_argument("--split", choices=["tuning", "test"], default="tuning")
    ans = sub.add_parser("evaluate-answers")
    ans.add_argument("--split", choices=["tuning", "test"], default="tuning")
    ans.add_argument("--max-questions", type=int)
    ans.add_argument("--question-ids", nargs="+")
    ans.add_argument("--prompts", nargs="+", help="Implemented development alternatives; no final-test override")
    plan = sub.add_parser("plan-answers", help="Write a no-call plan with coverage and request limits")
    plan.add_argument("--split", choices=["tuning", "test"], default="tuning")
    plan.add_argument("--max-questions", type=int)
    plan.add_argument("--question-ids", nargs="+")
    plan.add_argument("--prompts", nargs="+", help="Implemented development alternatives; no final-test override")
    review = sub.add_parser("review-answers", help="Validate completed judgments and summarize a paired run")
    review.add_argument("results", type=Path)
    review.add_argument("reviews", type=Path)
    review.add_argument("--whole-answer-reviews", type=Path,
                        help="Apply explicit whole-answer/export judgments; mandatory for selection")
    selection = sub.add_parser("select-generation", help="Validate development evidence and optionally apply its winner")
    selection.add_argument("--results", type=Path, nargs="+", required=True)
    selection.add_argument("--reviews", type=Path, nargs="+", required=True)
    selection.add_argument("--calibration", type=Path)
    selection.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.command == "check-runtime":
        from .preflight import inspect_runtime
        from .common import runtime_dir
        report = inspect_runtime()
        write_json(args.output or runtime_dir() / "runtime-preflight.json", report)
        emit_report(report)
    elif args.command == "ingest":
        from .corpus import ingest
        emit_report(ingest())
    elif args.command == "prepare-encoder":
        from .retrieval import prepare_encoder
        emit_report(prepare_encoder(allow_download=args.allow_download))
    elif args.command == "evaluate-local-matrix":
        from .experiments import generation_matrix
        if args.max_questions is not None and args.max_questions < 2:
            parser.error("Use at least two questions to cover answerable and unanswerable strata")
        report = generation_matrix(max_questions=args.max_questions, judge=not args.no_judge,
                                   calibration_path=args.calibration, question_ids=args.question_ids)
        emit_report(report)
    elif args.command == "calibrate-judge":
        from .experiments import calibrate_judge
        emit_report(calibrate_judge())
    elif args.command == "diagnose-answers":
        from .experiments import diagnose_with_reference_context
        emit_report(diagnose_with_reference_context(read_json(args.results), read_json(args.reviews) if args.reviews else None))
    elif args.command == "evaluate-rewrite":
        from .experiments import rewrite_experiment
        if args.max_questions is not None and args.max_questions < 1:
            parser.error("max-questions must be positive")
        emit_report(rewrite_experiment(max_questions=args.max_questions))
    elif args.command == "search":
        from .retrieval import Retriever
        hits = Retriever(read_documents(), load_config()).search(args.question)
        print(json.dumps(hits, indent=2))
    elif args.command == "evaluate-retrieval":
        from .evaluation import retrieval_evaluation
        report = retrieval_evaluation(args.methods, args.split)
        emit_report(report, ["status", "aggregates"])
    elif args.command == "plan-answers":
        from .evaluation import answer_plan
        report = answer_plan(args.split, args.max_questions, question_ids=args.question_ids, prompt_names=args.prompts)
        write_json(ROOT / "reports/answer-plan.json", report)
        emit_report(report, ["status", "covered_slices", "maximum_provider_requests", "maximum_output_tokens"])
    elif args.command == "review-answers":
        from .evaluation import summarize_answer_review
        report = summarize_answer_review(read_json(args.results), read_json(args.reviews))
        if args.whole_answer_reviews:
            from .whole_review import apply_whole_review
            report = apply_whole_review(read_json(args.results), report, read_json(args.whole_answer_reviews))
        else:
            report["whole_answer_reviewed"] = False
        write_json(args.results.parent / "review-summary.json", report)
        emit_report(report)
    elif args.command == "select-generation":
        from .experiments import select_generation
        emit_report(select_generation(args.results, args.reviews, apply=args.apply,
                                      calibration_path=args.calibration))
    else:
        from .evaluation import answer_evaluation
        if args.max_questions is not None and args.max_questions < 1:
            parser.error("max-questions must be positive")
        report = answer_evaluation(args.split, args.max_questions, question_ids=args.question_ids, prompt_names=args.prompts)
        emit_report(report, ["status", "run_directory", "actual_provider_requests"])


if __name__ == "__main__":
    main()
