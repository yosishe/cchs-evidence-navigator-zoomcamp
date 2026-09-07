"""Prepare a lineage-preserving BioC intake whose embedding rows fit the encoder."""
from __future__ import annotations

import argparse
import copy
import json
import os
import re
import shutil
import sys
import uuid
from pathlib import Path
from typing import Protocol

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from navigator.common import ROOT, digest, read_json, utc_now, write_json
from navigator.corpus import prepare
from navigator.retrieval import embedding_text


SOURCE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")


class TokenCounter(Protocol):
    """Small public seam used by the preparer and deterministic tests."""

    max_seq_length: int

    def count(self, text: str) -> int: ...


class SentenceTransformerTokenCounter:
    """Count exactly as the configured cached SentenceTransformer tokenizer does."""

    def __init__(self, cfg: dict, model_cache: Path):
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(
            cfg["embedding_model"],
            revision=cfg.get("embedding_revision"),
            cache_folder=str(model_cache),
            device=cfg.get("embedding_device", "cpu"),
            local_files_only=True,
        )
        self.max_seq_length = int(self.model.max_seq_length)
        if self.max_seq_length <= 0:
            raise ValueError("Encoder max_seq_length must be positive")

    def count(self, text: str) -> int:
        return len(self.model.tokenizer.encode(text, truncation=False))


def _absolute_unresolved(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path)))


def _symlink_component(path: Path) -> Path | None:
    absolute = _absolute_unresolved(path)
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current /= part
        if current.is_symlink():
            return current
    return None


def _overlaps(left: Path, right: Path) -> bool:
    left, right = left.resolve(), right.resolve()
    return left == right or left in right.parents or right in left.parents


def _regular_input(path: Path, label: str) -> Path:
    supplied = _absolute_unresolved(path)
    if _symlink_component(supplied):
        raise ValueError(f"{label} path has a symlink ancestor")
    resolved = supplied.resolve()
    if not resolved.is_file() or resolved.is_symlink():
        raise ValueError(f"{label} must be a regular, non-symlink file")
    return resolved


def _safe_raw_path(manifest_path: Path, raw_file: object, source_id: str) -> Path:
    if not isinstance(raw_file, str) or not raw_file or Path(raw_file).is_absolute():
        raise ValueError(f"Unsafe raw_file for {source_id}")
    relative = Path(raw_file)
    if any(part in {"", ".", ".."} for part in relative.parts):
        raise ValueError(f"Unsafe raw_file for {source_id}")
    candidate = manifest_path.parent
    for part in relative.parts:
        candidate /= part
        if candidate.is_symlink():
            raise ValueError(f"Source path contains a symlink: {source_id}")
    resolved = candidate.resolve()
    if manifest_path.parent.resolve() not in resolved.parents or not resolved.is_file():
        raise ValueError(f"Source snapshot is missing or escapes the manifest directory: {source_id}")
    return resolved


def _documents(raw: bytes, source_id: str) -> tuple[object, list[dict]]:
    try:
        obj = json.loads(raw)
        collections = obj if isinstance(obj, list) else [obj]
        documents = [document for collection in collections
                     for document in collection.get("documents", [])]
    except (json.JSONDecodeError, AttributeError, TypeError) as exc:
        raise ValueError(f"Invalid BioC JSON: {source_id}") from exc
    if len(documents) != 1 or documents[0].get("id") != source_id:
        raise ValueError(f"Unexpected BioC publication identity: {source_id}")
    passages = documents[0].get("passages")
    if not isinstance(passages, list):
        raise ValueError(f"Invalid BioC passages: {source_id}")
    return obj, passages


def _prefix(document: dict, template: str) -> str:
    if template == "content":
        return ""
    if template == "title_content":
        return document["title"] + "\n"
    if template == "title_heading_content":
        return document["title"] + "\n" + document.get("section_heading", "unknown") + "\n"
    raise ValueError("Unsupported embedding text template")


def _bounded_fragments(text: str, prefix: str, *, chunk_chars: int, overlap_chars: int,
                       counter: TokenCounter) -> list[tuple[int, int, str]]:
    """Return covering fragments using exhaustive backoff, without monotonicity assumptions."""
    if counter.count(prefix) >= counter.max_seq_length:
        raise ValueError("Unsplittable embedding prefix exceeds the encoder token budget")
    fragments: list[tuple[int, int, str]] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_chars, len(text))
        while end > start and counter.count(prefix + text[start:end]) > counter.max_seq_length:
            end -= 1
        if end == start:
            raise ValueError("Passage cannot fit one evidence character after its embedding prefix")
        fragments.append((start, end, text[start:end]))
        if end == len(text):
            break
        overlap = min(overlap_chars, end - start - 1)
        next_start = end - overlap
        if next_start <= start:
            raise ValueError("Token-bounded splitting failed to make progress")
        start = next_start
    return fragments


def _serialize_bioc(obj: object) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")


def _source_rows(rows: list[dict], source_id: str) -> list[dict]:
    return [row for row in rows if row["source_id"] == source_id]


def prepare_token_bounded_intake(
    manifest: Path,
    config: Path,
    destination: Path,
    model_cache: Path,
    *,
    token_counter: TokenCounter | None = None,
    active_package: Path = ROOT,
) -> dict:
    """Create a new self-contained manifest directory and return its validation receipt."""
    destination = _absolute_unresolved(Path(destination))
    if _symlink_component(destination):
        raise ValueError("Destination path has a symlink ancestor")
    if destination.exists() or destination.is_symlink():
        raise ValueError(f"Destination already exists: {destination}")

    manifest_path = _regular_input(Path(manifest), "Manifest")
    config_path = _regular_input(Path(config), "Config")
    active_package = _absolute_unresolved(Path(active_package)).resolve()
    destination_resolved = destination.resolve()
    if _overlaps(destination_resolved, manifest_path.parent):
        raise ValueError("Destination overlaps the input manifest directory")
    if _overlaps(destination_resolved, active_package):
        raise ValueError("Destination overlaps the active package")

    cfg = read_json(config_path)
    if not isinstance(cfg, dict):
        raise ValueError("Config must be a JSON object")
    chunk_chars, overlap_chars = cfg.get("chunk_chars"), cfg.get("overlap_chars")
    if (not isinstance(chunk_chars, int) or isinstance(chunk_chars, bool)
            or not isinstance(overlap_chars, int) or isinstance(overlap_chars, bool)
            or not 0 <= overlap_chars < chunk_chars):
        raise ValueError("Invalid overlapping chunk configuration")
    template = cfg.get("embedding_text", "title_content")

    requested_manifest = read_json(manifest_path)
    if not isinstance(requested_manifest, dict) or not isinstance(requested_manifest.get("sources"), list):
        raise ValueError("Manifest must contain a sources list")
    raw_by_id: dict[str, bytes] = {}
    ids: set[str] = set()
    for source in requested_manifest["sources"]:
        if not isinstance(source, dict):
            raise ValueError("Every manifest source must be an object")
        source_id = source.get("source_id")
        if not isinstance(source_id, str) or not SOURCE_ID.fullmatch(source_id):
            raise ValueError(f"Unsafe source_id: {source_id!r}")
        if source_id in ids:
            raise ValueError(f"Duplicate source_id: {source_id}")
        ids.add(source_id)
        if source.get("status") != "included":
            continue
        raw_path = _safe_raw_path(manifest_path, source.get("raw_file"), source_id)
        raw = raw_path.read_bytes()
        if digest(raw) != source.get("sha256"):
            raise ValueError(f"Source hash mismatch: {source_id}")
        _documents(raw, source_id)
        raw_by_id[source_id] = raw

    # This validates hashes, publication identities, and the existing corpus window contract.
    original_rows, _, validated_manifest = prepare(manifest_path=manifest_path, cfg=cfg)

    cache_path = _absolute_unresolved(Path(model_cache))
    if _symlink_component(cache_path):
        raise ValueError("Model cache path has a symlink ancestor")
    if not cache_path.resolve().is_dir():
        raise ValueError("Model cache must be an existing, non-symlink directory")
    counter = token_counter or SentenceTransformerTokenCounter(cfg, cache_path.resolve())
    if (not isinstance(counter.max_seq_length, int) or isinstance(counter.max_seq_length, bool)
            or counter.max_seq_length <= 0):
        raise ValueError("Token counter max_seq_length must be a positive integer")

    overflow_rows = [row for row in original_rows
                     if counter.count(embedding_text(row, template)) > counter.max_seq_length]
    affected_passages: dict[str, set[int]] = {}
    for row in overflow_rows:
        affected_passages.setdefault(row["source_id"], set()).add(row["passage_index"])

    output_manifest = copy.deepcopy(validated_manifest)
    output_raw: dict[str, bytes] = dict(raw_by_id)
    for source in output_manifest["sources"]:
        source_id = source["source_id"]
        if source.get("status") != "included":
            continue
        source["raw_file"] = f"raw/{source_id}.json"
        indexes = affected_passages.get(source_id)
        if not indexes:
            continue

        obj, passages = _documents(raw_by_id[source_id], source_id)
        rows_by_index: dict[int, dict] = {}
        for row in original_rows:
            if row["source_id"] == source_id and row["passage_index"] in indexes:
                rows_by_index.setdefault(row["passage_index"], row)
        transformed: list[dict] = []
        replacement_passages: list[dict] = []
        for index, passage in enumerate(passages):
            if index not in indexes:
                replacement_passages.append(passage)
                continue
            text = passage.get("text", "")
            if not isinstance(text, str):
                raise ValueError(f"Invalid BioC passage text: {source_id}:{index}")
            infons = passage.get("infons", {})
            if not isinstance(infons, dict):
                raise ValueError(f"Invalid BioC passage infons: {source_id}:{index}")
            prefix = _prefix(rows_by_index[index], template)
            fragments = _bounded_fragments(
                text, prefix, chunk_chars=chunk_chars, overlap_chars=overlap_chars,
                counter=counter,
            )
            parent_offset = passage.get("offset", 0)
            if not isinstance(parent_offset, int) or isinstance(parent_offset, bool):
                raise ValueError(f"Invalid BioC passage offset: {source_id}:{index}")
            for start, end, content in fragments:
                derived = copy.deepcopy(passage)
                derived["text"] = content
                derived["offset"] = parent_offset + start
                for annotation_field in ("sentences", "annotations", "relations"):
                    if annotation_field in derived:
                        derived[annotation_field] = []
                derived_index = len(replacement_passages)
                replacement_passages.append(derived)
                transformed.append({
                    "operation": "split_overflowing_bioc_passage",
                    "original_passage_index": index,
                    "derived_passage_index": derived_index,
                    "original_start": start,
                    "original_end": end,
                    "adjusted_bioc_offset": derived["offset"],
                    "inherited_infons": copy.deepcopy(infons),
                })
        passages[:] = replacement_passages
        bounded = _serialize_bioc(obj)
        output_raw[source_id] = bounded
        parent_hash = digest(raw_by_id[source_id])
        source["sha256"] = digest(bounded)
        source["token_bounded_intake"] = {
            "parent_snapshot": f"parents/{source_id}.json",
            "parent_snapshot_sha256": parent_hash,
            "path_semantics": "Paths are relative to this manifest directory.",
            "embedding_text": template,
            "max_seq_length": counter.max_seq_length,
            "chunk_chars": chunk_chars,
            "overlap_chars": overlap_chars,
            "transforms": transformed,
        }

    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = destination.parent / f".{destination.name}.staging-{uuid.uuid4().hex}"
    try:
        staging.mkdir()
        (staging / "raw").mkdir()
        for source_id, raw in output_raw.items():
            (staging / "raw" / f"{source_id}.json").write_bytes(raw)
        if affected_passages:
            (staging / "parents").mkdir()
            for source_id in sorted(affected_passages):
                (staging / "parents" / f"{source_id}.json").write_bytes(raw_by_id[source_id])
        write_json(staging / "manifest.json", output_manifest)
        shutil.copy2(config_path, staging / "config.json")

        output_rows, _, on_disk_manifest = prepare(staging / "manifest.json", cfg=cfg)
        remaining = [row for row in output_rows
                     if counter.count(embedding_text(row, template)) > counter.max_seq_length]
        if remaining:
            raise ValueError(f"Token-bounded verification found {len(remaining)} overflowing rows")
        unchanged = sorted(set(raw_by_id) - set(affected_passages))
        for source_id in unchanged:
            if _source_rows(output_rows, source_id) != _source_rows(original_rows, source_id):
                raise ValueError(f"Unchanged source rows changed: {source_id}")
        for source_id in affected_passages:
            output_source = next(source for source in on_disk_manifest["sources"]
                                 if source["source_id"] == source_id)
            lineage = output_source["token_bounded_intake"]
            parent_obj, parent_passages = _documents(raw_by_id[source_id], source_id)
            del parent_obj
            bounded_bytes = (staging / output_source["raw_file"]).read_bytes()
            _, bounded_passages = _documents(bounded_bytes, source_id)
            coverage: dict[int, list[tuple[int, int]]] = {}
            for item in lineage["transforms"]:
                parent_text = parent_passages[item["original_passage_index"]]["text"]
                start, end = item["original_start"], item["original_end"]
                if not (0 <= start < end <= len(parent_text)):
                    raise ValueError(f"Invalid lineage offsets: {source_id}")
                derived = bounded_passages[item["derived_passage_index"]]
                if (derived.get("text") != parent_text[start:end]
                        or derived.get("offset") != item["adjusted_bioc_offset"]):
                    raise ValueError(f"Derived passage does not match its parent quote: {source_id}")
                coverage.setdefault(item["original_passage_index"], []).append((start, end))
            for original_index, spans in coverage.items():
                spans.sort()
                parent_text = parent_passages[original_index]["text"]
                if (spans[0][0] != 0 or spans[-1][1] != len(parent_text)
                        or any(current[0] > previous[1]
                               for previous, current in zip(spans, spans[1:]))):
                    raise ValueError(f"Derived passages omit parent evidence characters: {source_id}")

        receipt = {
            "status": "TOKEN_BOUNDED_INTAKE_PREPARED_NOT_QUALITY_EVALUATED",
            "created_at": utc_now(),
            "source_manifest": str(manifest_path),
            "source_manifest_sha256": digest(validated_manifest),
            "source_config": str(config_path),
            "source_config_sha256": digest(cfg),
            "model_cache": str(cache_path.resolve()),
            "local_files_only": True,
            "embedding_model": cfg.get("embedding_model"),
            "embedding_revision": cfg.get("embedding_revision"),
            "embedding_text": template,
            "max_seq_length": counter.max_seq_length,
            "overflow_rows_before": len(overflow_rows),
            "overflow_rows_after": 0,
            "affected_sources": sorted(affected_passages),
            "unchanged_sources": unchanged,
            "unchanged_source_rows_verified": sum(
                len(_source_rows(original_rows, source_id)) for source_id in unchanged
            ),
            "output_manifest_sha256": digest(on_disk_manifest),
            "output_corpus_sha256": digest(output_rows),
            "downloads_performed": False,
            "quality_evaluation_performed": False,
            "promotion_performed": False,
        }
        write_json(staging / "token-bounded-intake.json", receipt)
        if destination.exists():
            raise ValueError(f"Destination already exists: {destination}")
        staging.rename(destination)
        return receipt
    except Exception:
        if staging.exists():
            shutil.rmtree(staging)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--destination", required=True, type=Path)
    parser.add_argument("--model-cache", required=True, type=Path)
    args = parser.parse_args()
    receipt = prepare_token_bounded_intake(
        args.manifest, args.config, args.destination, args.model_cache
    )
    print(json.dumps(receipt, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
