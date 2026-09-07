"""Original project contracts; Python file/config patterns from course Module 1."""
from __future__ import annotations

import hashlib
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(value) -> str:
    raw = value if isinstance(value, bytes) else json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode()
    return hashlib.sha256(raw).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def runtime_code_id():
    """Hash shipped Python code, excluding generated reports and selection metadata."""
    paths = [ROOT / "app.py", *sorted((ROOT / "navigator").glob("*.py"))]
    return digest({str(path.relative_to(ROOT)): digest(path.read_bytes()) for path in paths})


def effective_config(config):
    """Selection evidence may refer to a config without recursively hashing itself."""
    metadata = {"selection_status", "generation_selection_status", "generation_selection_artifact"}
    return {key: value for key, value in config.items() if key not in metadata}


def verify_generation_selection(config):
    if not config.get("generation_selection_status", "").startswith("SELECTED"):
        raise ValueError("Generation is still a candidate")
    path = config.get("generation_selection_artifact")
    if not path:
        raise ValueError("Selected generation has no evidence artifact")
    evidence = read_json(ROOT / path)
    if (evidence.get("status") != "SELECTED_ON_PROVISIONAL_AGENT_REVIEW"
            or evidence.get("effective_config_id") != digest(effective_config(config))
            or evidence.get("runtime_code_id") != runtime_code_id()):
        raise ValueError("Selected generation differs from its evidence/configuration/code")
    for reference in evidence["inputs"]:
        for field in ("results", "reviews", "whole_reviews"):
            if not reference.get(field + "_path") or not reference.get(field + "_hash"):
                raise ValueError("Selection is missing required whole-answer or primary evidence")
            if digest(read_json(ROOT / reference[field + "_path"])) != reference[field + "_hash"]:
                raise ValueError("Selection input changed after evaluation")
        calibration = reference.get("calibration")
        if calibration:
            calibration_path = ROOT / calibration["path"]
            artifact = read_json(calibration_path)
            if (digest(artifact) != calibration["artifact_hash"]
                    or digest(read_json(calibration_path.parent / "fixtures.json")) != artifact["fixtures_hash"]
                    or digest(read_json(calibration_path.parent / "reviews.json")) != artifact["reviews_hash"]):
                raise ValueError("Selection calibration evidence changed after evaluation")
    return evidence


def runtime_dir():
    return Path(os.getenv("NAVIGATOR_RUNTIME", str(ROOT / "runtime")))


def model_cache_dir():
    # Shared per project, independent of temporary ingestion/telemetry test data.
    return Path(os.getenv("NAVIGATOR_MODEL_CACHE", str(ROOT / "runtime/models")))


def load_config(path: Path | None = None):
    cfg = read_json(path or Path(os.getenv("NAVIGATOR_CONFIG", str(ROOT / "configs/app.json"))))
    # Normalize the override into the fingerprinted configuration: changing a
    # timeout cannot silently reuse selection evidence from another run.
    timeout = os.getenv("NAVIGATOR_REQUEST_TIMEOUT")
    if timeout:
        parsed_timeout = float(timeout)
        cfg["request_timeout_seconds"] = int(parsed_timeout) if parsed_timeout.is_integer() else parsed_timeout
    timeout = cfg.get("request_timeout_seconds", 120)
    if (isinstance(timeout, bool) or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout) or timeout <= 0):
        raise ValueError("request_timeout_seconds must be finite and positive")
    if type(cfg.get("json_mode", True)) is not bool:
        raise ValueError("json_mode must be a boolean")
    if cfg["retrieval"] not in {"lexical", "vector", "hybrid"}:
        raise ValueError("Unsupported retrieval configuration")
    if not 0 < cfg["top_k"] <= cfg["candidate_k"]:
        raise ValueError("top_k must be positive and no greater than candidate_k")
    if cfg["rrf_k"] <= 0:
        raise ValueError("rrf_k must be positive for zero-based course RRF")
    if not 0 <= cfg["overlap_chars"] < cfg["chunk_chars"]:
        raise ValueError("Invalid overlapping chunk configuration")
    if cfg["prompt"] not in {"concise", "evidence_first", "coverage_first", "course_user", "schema_first", "plain_context", "short_ids", "compact_metadata"}:
        raise ValueError("Unknown prompt configuration")
    if cfg.get("embedding_text", "title_content") not in {"content", "title_content", "title_heading_content"}:
        raise ValueError("Unknown embedding text template")
    fields = cfg.get("lexical_fields", ["title", "section", "content"])
    if (not isinstance(fields, list) or not all(isinstance(f, str) for f in fields)
            or len(set(fields)) != len(fields) or "content" not in fields
            or not set(fields) <= {"title", "section", "section_heading", "content"}):
        raise ValueError("Invalid lexical fields")
    return cfg


def read_documents(path: Path | None = None):
    p = path or runtime_dir() / "documents.jsonl"
    if path is None:
        report = read_json(runtime_dir() / "ingestion-report.json")
        if digest(p.read_bytes()) != report["documents_sha256"]:
            raise ValueError("Active corpus differs from the recorded ingestion artifact")
    docs = [json.loads(line) for line in p.read_text().splitlines() if line.strip()]
    if not docs or len({d["id"] for d in docs}) != len(docs):
        raise ValueError("Corpus is empty or contains duplicate chunk IDs")
    return docs


def csv_safe(value):
    """Preserve raw evidence in JSON; neutralize spreadsheet formulas in CSV export."""
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + value
    return value
