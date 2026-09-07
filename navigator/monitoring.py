"""Module 5 pandas aggregations with explicit origin and feedback denominators."""
import pandas as pd

ORIGINS = ("user", "qa", "evaluation", "legacy_unknown")


def observed_tables(answers, feedback, origin="user", mode="all"):
    if origin not in (*ORIGINS, "all") or mode not in {"all", "llm", "evidence_preview"}:
        raise ValueError("Invalid monitoring scope")
    selected = [r for r in answers
                if (origin == "all" or r.get("traffic_origin", "legacy_unknown") == origin)
                and (mode == "all" or r["mode"] == mode)]
    if not selected:
        return None
    frame = pd.DataFrame(selected)
    if frame["id"].duplicated().any():
        raise ValueError("Duplicate answer identity in monitoring input")
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
    frame["time_utc"] = frame["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    answer_origins = {r["id"]: r.get("traffic_origin", "legacy_unknown") for r in selected}
    scoped_feedback = [r for r in feedback if r["answer_id"] in answer_origins]
    mismatched = [r for r in scoped_feedback
                  if r.get("traffic_origin", "legacy_unknown") != answer_origins[r["answer_id"]]]
    ratings = {r["answer_id"]: r for r in scoped_feedback
               if r.get("traffic_origin", "legacy_unknown") == answer_origins[r["answer_id"]]}
    tokens = frame.dropna(subset=["input_tokens", "output_tokens"])
    return {
        "requests": len(frame), "rated_requests": len(ratings),
        "excluded_mismatched_feedback": len(mismatched),
        "volume": frame.groupby(frame["timestamp"].dt.strftime("%Y-%m-%d UTC")).size().rename("requests"),
        "generation_seconds": frame.set_index("time_utc")[["seconds"]],
        "passage_counts": frame.assign(passages=[len(r["retrieved_ids"]) for r in selected]).set_index("id")[["passages"]],
        "feedback": pd.Series(["Helpful" if r["score"] == 1 else "Not helpful" for r in ratings.values()], dtype="object").value_counts().rename("rated requests"),
        "outcomes": frame["status"].value_counts().rename("requests"),
        "tokens": tokens.groupby("model")[["input_tokens", "output_tokens"]].sum() if not tokens.empty else None,
    }
