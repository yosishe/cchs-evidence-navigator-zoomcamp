"""Bounded research prototype, not a selectable application generation path."""
import copy
import json
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from navigator.common import ROOT, digest, read_json, runtime_code_id, utc_now, write_json
from navigator.providers import complete, model_identity, IncompleteModelOutput
from navigator.rag import validate_answer
from navigator.whole_review import export_payload, whole_review_template


def attach_source_windows(raw, hits):
    """Exact source lookup; does not assert that the source entails a claim."""
    value = json.loads(raw)
    if not isinstance(value, dict) or set(value) != {"status", "claims", "limitations"}:
        raise ValueError("Unexpected prototype output fields")
    if not isinstance(value["claims"], list):
        raise ValueError("Claims must be a list")
    lookup = {f"E{i}": hit for i, hit in enumerate(hits, 1)}
    claims = []
    for claim in value["claims"]:
        if not isinstance(claim, dict) or set(claim) != {"text", "evidence_id"}:
            raise ValueError("Model may author only claim text and the selected label")
        label = claim["evidence_id"]
        if not isinstance(label, str) or label not in lookup:
            raise ValueError("Unknown request-local source label")
        hit = lookup[label]
        claims.append({"text": claim["text"], "evidence_id": hit["id"],
                       "exact_quote": hit["content"]})
    return validate_answer({"status": value["status"], "claims": claims,
                            "limitations": value["limitations"]}, hits)


def check_adapter():
    hit = {"id": "fictional-source:window", "content": "Ten adults were observed."}
    good = {"status": "answered", "claims": [{"text": "Ten adults were observed.",
            "evidence_id": "E1"}], "limitations": "Synthetic interface check."}
    answer = attach_source_windows(json.dumps(good), [hit])
    assert answer["claims"][0]["exact_quote"] == hit["content"]
    assert answer["claims"][0]["evidence_id"] == hit["id"]
    for bad in [{"evidence_id": "E2"}, {"evidence_id": hit["id"]},
                {"exact_quote": "Invented quote"}, {"source_url": "injected"}]:
        payload = copy.deepcopy(good)
        payload["claims"][0].update(bad)
        try:
            attach_source_windows(json.dumps(payload), [hit])
        except ValueError:
            continue
        raise AssertionError("Invalid/foreign model field accepted")
    false_claim = copy.deepcopy(good)
    false_claim["claims"][0]["text"] = "No adults were observed."
    # Mechanically valid but false: semantic review must still veto this answer.
    assert attach_source_windows(json.dumps(false_claim), [hit])["claims"]


def run(plan_path=None):
    check_adapter()
    itpath = Path(plan_path) if plan_path else ROOT / "reports/goal-loop/iterations/015-source-attached-prototype.json"
    plan = read_json(itpath)
    if plan["status"] != "PLANNED":
        raise RuntimeError("Do not restart an already dispatched prototype")
    cfg = {**plan["config"], "prompt": "prototype_source_attached"}
    identity = model_identity(cfg)
    original = read_json(ROOT / plan["source_run"])
    folder = ROOT / "reports/goal-loop" / ("source-attached-prototype-" + str(uuid.uuid4()))
    report = {"created_at": utc_now(), "status": "RUNNING", "split": "source_attachment_diagnostic",
              "scope": "PROTOTYPE_NOT_APPLICATION_OR_SELECTION_EVIDENCE",
              "runtime_code_id": runtime_code_id(), "prototype_code_id": digest(Path(__file__).read_bytes()),
              "config": cfg, "config_id": digest(cfg), "model_identity": identity,
              "questions": original["questions"], "prompts": [cfg["prompt"]],
              "per_question": [], "actual_provider_requests": 0, "official_points": None}
    plan.update(status="RUNNING", run_directory=str(folder.relative_to(ROOT)))
    write_json(itpath, plan)
    write_json(folder / "plan.json", plan)
    (folder / "prototype-source.py").write_bytes(Path(__file__).read_bytes())
    write_json(folder / "results.json", report)
    for q in report["questions"]:
        if runtime_code_id() != report["runtime_code_id"]:
            raise RuntimeError("Runtime changed during prototype")
        model_identity(cfg)
        old = next(x["record"] for x in original["per_question"]
                   if x["question_id"] == q["id"] and x["prompt"] == "evidence_first")
        passages = json.loads(old["context"])
        for i, passage in enumerate(passages, 1):
            passage["evidence_id"] = f"E{i}"
            passage.pop("source_version")
            passage.pop("source_url")
        messages = [{"role": "system", "content": plan["instructions"]},
                    {"role": "user", "content": json.dumps({"question": q["question"], "passages": passages})}]
        rec = {"id": str(uuid.uuid4()), "timestamp": utc_now(), "mode": "llm", "prototype_only": True,
               "question": q["question"], "config": cfg, "config_id": digest(cfg),
               "corpus_id": old["corpus_id"], "runtime_code_id": report["runtime_code_id"],
               "hits": copy.deepcopy(old["hits"]), "context": old["context"], "context_id": old["context_id"],
               "instructions": plan["instructions"], "calls": [], "status": "started", "claims": [],
               "limitations": "", "quote_selection_method": "application_full_source_window",
               "support_review": "PENDING_AGENT_REVIEW", "scientific_review": "PENDING_HUMAN_REVIEW"}
        stop = False
        try:
            raw = complete(cfg, messages, stage="generation", ledger=rec["calls"])
            rec["raw_output"] = raw
            rec.update(attach_source_windows(raw, rec["hits"]))
        except (ValueError, TypeError, KeyError) as exc:
            rec.update(status="error", error_stage="output_validation", error_type=type(exc).__name__,
                       claims=[], limitations="The prototype output failed validation; no claims are exported.")
        except Exception as exc:
            stop = True
            rec.update(status="error", error_stage="provider", error_type=type(exc).__name__,
                       claims=[], limitations="The local prototype request failed; no claims are exported.")
        call = rec["calls"][-1] if rec["calls"] else {}
        for key in ["raw_output", "input_tokens", "output_tokens", "seconds"]:
            rec[key] = call.get(key)
        rec["cost_usd"] = 0.0
        report["per_question"].append({"question_id": q["id"], "answerable": q["answerable"],
             "prompt": cfg["prompt"], "record": rec, "record_hash": digest(rec)})
        report["actual_provider_requests"] += len(rec["calls"])
        write_json(folder / "results.json", report)
        if stop:
            report["status"] = "STOPPED_ON_ERROR"
            break
    else:
        report["status"] = "EXECUTED_AWAITING_REVIEW"
    report["completed_at"] = utc_now()
    write_json(folder / "results.json", report)
    write_json(folder / "whole-answer-review-template.json", whole_review_template(report))
    write_json(folder / "export-adapter-payloads.json", {
        "scope": "Adapter payload inspection, not browser downloads. Integration must expose quote ownership/scope in each exported row.",
        "quote_selection_method": "application_full_source_window",
        "answers": [{"answer_id": row["record"]["id"], "payload": export_payload(row["record"])}
                    for row in report["per_question"]]})
    print({"status": report["status"], "run_directory": str(folder.relative_to(ROOT)),
           "actual_provider_requests": report["actual_provider_requests"]})


if __name__ == "__main__":
    if "--check" in sys.argv:
        check_adapter()
        print("Synthetic attachment boundaries passed; no semantic quality claim.")
    else:
        run(sys.argv[sys.argv.index("--plan") + 1] if "--plan" in sys.argv else None)
