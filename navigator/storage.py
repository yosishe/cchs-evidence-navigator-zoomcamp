"""Module 5 PostgreSQL/psycopg; explicit JSONL development adapter."""
from __future__ import annotations

import json
import os
import uuid
from pathlib import Path

from .common import runtime_dir, utc_now


class Journal:
    """Local development only. Never silently replace an unavailable PostgreSQL DB."""
    def __init__(self, path=None):
        self.path = Path(path) if path else runtime_dir() / "events.jsonl"

    def _transaction(self, kind, record):
        import fcntl
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a+") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            f.seek(0)
            events = [json.loads(line) for line in f if line.strip()]
            if any(e["kind"] == kind and e["record"]["id"] == record["id"] for e in events):
                return
            if kind == "feedback":
                answer = next((e["record"] for e in events if e["kind"] == "answer"
                               and e["record"]["id"] == record["answer_id"]), None)
                validate_feedback_origin(answer, record)
            f.seek(0, 2)
            f.write(json.dumps({"kind": kind, "record": record}, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())

    def save_answer(self, record):
        self._transaction("answer", record)

    def save_feedback(self, answer_id, score, comment="", feedback_id=None, *, traffic_origin="user"):
        rec = feedback_record(answer_id, score, comment, feedback_id, traffic_origin)
        self._transaction("feedback", rec)

    def read(self):
        if not self.path.exists():
            return [], []
        import fcntl
        with self.path.open() as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            events = [json.loads(line) for line in f if line.strip()]
        return ([e["record"] for e in events if e["kind"] == "answer"],
                [e["record"] for e in events if e["kind"] == "feedback"])


def feedback_record(answer_id, score, comment, feedback_id, traffic_origin="user"):
    if traffic_origin not in {"user", "qa", "evaluation"}:
        raise ValueError("Unknown feedback origin")
    if type(score) is not int or score not in {-1, 1}:
        raise ValueError("Feedback must be +1 or -1")
    if len(comment) > 2000:
        raise ValueError("Feedback comment is too long")
    return {"id": feedback_id or str(uuid.uuid4()), "answer_id": answer_id,
            "score": score, "comment": comment, "timestamp": utc_now(),
            "source": traffic_origin, "traffic_origin": traffic_origin}


def validate_feedback_origin(answer, feedback):
    if answer is None:
        raise ValueError("Feedback refers to an unknown answer")
    if answer.get("traffic_origin", "legacy_unknown") != feedback["traffic_origin"]:
        raise ValueError("Feedback origin must match the recorded answer origin")


class Postgres:
    def __init__(self):
        import psycopg
        self.psycopg = psycopg

    def connect(self):
        return self.psycopg.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            dbname=os.getenv("POSTGRES_DB", "evidence"),
            user=os.getenv("POSTGRES_USER", "evidence"),
            password=os.environ["POSTGRES_PASSWORD"], connect_timeout=5)

    def initialize(self):
        with self.connect() as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS answers (id TEXT PRIMARY KEY, payload JSONB NOT NULL)")
            conn.execute("CREATE TABLE IF NOT EXISTS feedback (id TEXT PRIMARY KEY, answer_id TEXT NOT NULL REFERENCES answers(id), payload JSONB NOT NULL)")

    def save_answer(self, record):
        with self.connect() as conn:
            conn.execute("INSERT INTO answers (id,payload) VALUES (%s,%s::jsonb) ON CONFLICT (id) DO NOTHING", (record["id"], json.dumps(record)))

    def save_feedback(self, answer_id, score, comment="", feedback_id=None, *, traffic_origin="user"):
        rec = feedback_record(answer_id, score, comment, feedback_id, traffic_origin)
        with self.connect() as conn:
            row = conn.execute("SELECT payload FROM answers WHERE id = %s FOR SHARE", (answer_id,)).fetchone()
            validate_feedback_origin(row[0] if row else None, rec)
            conn.execute("INSERT INTO feedback (id,answer_id,payload) VALUES (%s,%s,%s::jsonb) ON CONFLICT (id) DO NOTHING", (rec["id"], answer_id, json.dumps(rec)))

    def read(self):
        with self.connect() as conn:
            answers = [r[0] for r in conn.execute("SELECT payload FROM answers ORDER BY payload->>'timestamp'")]
            feedback = [r[0] for r in conn.execute("SELECT payload FROM feedback ORDER BY payload->>'timestamp'")]
        return answers, feedback


def get_store():
    mode = os.getenv("TELEMETRY_BACKEND", "jsonl")
    if mode == "postgres":
        store = Postgres()
        store.initialize()
        return store
    if mode == "jsonl":
        return Journal()
    raise ValueError("Unknown telemetry backend")
