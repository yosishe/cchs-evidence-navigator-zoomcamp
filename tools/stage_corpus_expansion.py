"""Build an isolated, validated corpus-expansion candidate package."""
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

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from navigator.common import ROOT, digest, read_json, utc_now, write_json
from navigator.corpus import prepare


PACKAGE_DIRECTORIES = ("navigator", "tests", "tools", "docs", "configs", "data", "reports")
ROOT_FILES = {
    ".dockerignore", ".env.example", ".gitignore", "Dockerfile", "README.md",
    "app.py", "compose.yaml", "pyproject.toml", "uv.lock",
}
EXCLUDED_NAMES = {
    ".git", ".venv", ".cache", ".pytest_cache", "__pycache__", "runtime",
    "weights", "models", "cache", "caches", "node_modules", ".dlt", "dlt",
}
EXCLUDED_ARTIFACT_SUFFIXES = {
    ".7z", ".bin", ".ckpt", ".db", ".duckdb", ".gguf", ".gz", ".h5",
    ".joblib", ".npy", ".npz", ".onnx", ".parquet", ".pdf", ".pickle",
    ".pkl", ".pt", ".pth", ".safetensors", ".sqlite", ".sqlite3", ".tar",
    ".tgz", ".zip",
}
SOURCE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")
RECEIPT_PATH = Path("reports/corpus-expansion-staging.json")
QUESTION_BANK = "data/evaluation/expansion-development.json"


def _overlaps(left: Path, right: Path) -> bool:
    left = left.resolve()
    right = right.resolve()
    return left == right or left in right.parents or right in left.parents


def _absolute_unresolved(path: Path) -> Path:
    """Make a lexical absolute path without following symlinks."""
    return Path(os.path.abspath(os.fspath(path)))


def _symlink_component(path: Path) -> Path | None:
    absolute = _absolute_unresolved(path)
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current /= part
        if current.is_symlink():
            return current
    return None


def _is_excluded(relative: Path) -> bool:
    if relative == Path(".env.example"):
        return False
    if any(part.casefold() in EXCLUDED_NAMES or part.casefold().endswith(".egg-info")
           for part in relative.parts):
        return True
    name = relative.name.casefold()
    return (name == ".ds_store" or name == ".env" or name.startswith(".env.")
            or name.endswith(".pyc") or name.endswith(".duckdb-wal")
            or relative.suffix.casefold() in EXCLUDED_ARTIFACT_SUFFIXES)


def package_files(package_root: Path) -> list[Path]:
    """Return the small, reviewable package allowlist; useful as a test seam."""
    root = Path(package_root).resolve()
    selected: list[Path] = []
    for name in sorted(ROOT_FILES | {p.name for p in root.glob("requirements*.lock")}):
        path = root / name
        if path.is_file() and not path.is_symlink():
            selected.append(Path(name))
    for directory in PACKAGE_DIRECTORIES:
        base = root / directory
        if not base.is_dir() or base.is_symlink():
            continue
        for current, directories, files in os.walk(base, followlinks=False):
            current_path = Path(current)
            directories[:] = sorted(
                name for name in directories
                if not (current_path / name).is_symlink()
                and not _is_excluded((current_path / name).relative_to(root))
            )
            for name in sorted(files):
                path = current_path / name
                relative = path.relative_to(root)
                if not path.is_symlink() and not _is_excluded(relative):
                    selected.append(relative)
    if not selected:
        raise ValueError("The active package allowlist is empty")
    if len(selected) != len(set(selected)):
        raise ValueError("The package allowlist contains duplicate paths")
    return sorted(selected)


def _runtime_code_id(root: Path) -> str:
    paths = [root / "app.py", *sorted((root / "navigator").glob("*.py"))]
    if not paths[0].is_file():
        raise ValueError("The package has no app.py runtime entry point")
    return digest({str(path.relative_to(root)): digest(path.read_bytes())
                   for path in paths if path.is_file() and not path.is_symlink()})


def _safe_raw_path(manifest_path: Path, raw_file: object, source_id: str) -> Path:
    if not isinstance(raw_file, str) or not raw_file or Path(raw_file).is_absolute():
        raise ValueError(f"Unsafe raw_file for {source_id}")
    relative = Path(raw_file)
    if any(part in {"", ".", ".."} for part in relative.parts):
        raise ValueError(f"Unsafe raw_file for {source_id}")
    current = manifest_path.parent
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"Source path contains a symlink: {source_id}")
    resolved = current.resolve()
    if manifest_path.parent.resolve() not in resolved.parents:
        raise ValueError(f"Source path escapes the manifest directory: {source_id}")
    if not resolved.is_file():
        raise ValueError(f"Source snapshot is missing: {source_id}")
    return resolved


def _publication_content(raw: bytes, source_id: str) -> str:
    try:
        obj = json.loads(raw)
        collections = obj if isinstance(obj, list) else [obj]
        documents = [document for collection in collections
                     for document in collection.get("documents", [])]
    except (json.JSONDecodeError, AttributeError, TypeError) as exc:
        raise ValueError(f"Invalid BioC JSON: {source_id}") from exc
    if len(documents) != 1:
        # prepare() will also enforce this, but a clear error belongs to pre-copy validation.
        raise ValueError(f"Unexpected BioC publication identity: {source_id}")
    passages = documents[0].get("passages", [])
    if not isinstance(passages, list):
        raise ValueError(f"Invalid BioC passages: {source_id}")
    # Publication wrappers, IDs, annotations, and offsets can differ while the
    # actual publication text is duplicated. Compare the ordered source text.
    return digest([passage.get("text", "") for passage in passages])


def _canonical_publication_identifier(field: str, value: object) -> str:
    text = str(value).strip()
    if field == "doi":
        text = re.sub(r"(?i)^(?:doi\s*:\s*|https?://(?:dx\.)?doi\.org/)", "", text)
        text = text.rstrip("/")
    elif field == "pmid":
        text = re.sub(r"(?i)^pmid\s*:\s*", "", text)
    elif field == "pmcid":
        text = re.sub(r"(?i)^pmcid\s*:\s*", "", text)
    elif field == "article_url":
        text = text.rstrip("/")
    return text.casefold()


def _validated_inputs(manifest_path: Path, cfg: dict) -> tuple[dict, dict[str, bytes], list[dict], str]:
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise ValueError("Manifest must be a regular, non-symlink file")
    manifest = read_json(manifest_path)
    if not isinstance(manifest, dict) or not isinstance(manifest.get("sources"), list):
        raise ValueError("Manifest must contain a sources list")

    ids: set[str] = set()
    publication_keys: dict[tuple[str, str], str] = {}
    content_keys: dict[str, str] = {}
    raw_by_id: dict[str, bytes] = {}
    copied_sources: list[dict] = []
    for source in manifest["sources"]:
        if not isinstance(source, dict):
            raise ValueError("Every manifest source must be an object")
        source_id = source.get("source_id")
        if not isinstance(source_id, str) or not SOURCE_ID.fullmatch(source_id):
            raise ValueError(f"Unsafe source_id: {source_id!r}")
        if source_id in ids:
            raise ValueError(f"Duplicate source_id: {source_id}")
        ids.add(source_id)
        status = source.get("status")
        if status not in {"included", "blocked"}:
            raise ValueError(f"Unsupported source status: {source_id}")
        if status == "blocked":
            continue

        raw_path = _safe_raw_path(manifest_path, source.get("raw_file"), source_id)
        raw = raw_path.read_bytes()
        raw_by_id[source_id] = raw
        copied_sources.append({"source_id": source_id, "sha256": digest(raw)})
        for field in ("pmcid", "pmid", "doi", "article_url"):
            value = source.get(field)
            if value is None or not str(value).strip():
                continue
            canonical = _canonical_publication_identifier(field, value)
            if not canonical:
                continue
            key = (field, canonical)
            if key in publication_keys:
                raise ValueError(f"Duplicate publication identifier: {source_id} and {publication_keys[key]}")
            publication_keys[key] = source_id
        content_key = _publication_content(raw, source_id)
        if content_key in content_keys:
            raise ValueError(f"Duplicate publication content: {source_id} and {content_keys[content_key]}")
        content_keys[content_key] = source_id

    # This is the existing authoritative hash, BioC identity, window, and nonempty validation seam.
    rows, _, validated_manifest = prepare(manifest_path=manifest_path, cfg=cfg)
    return validated_manifest, raw_by_id, copied_sources, digest(rows)


def _copy_package(root: Path, staging: Path, files: list[Path]) -> None:
    for relative in files:
        # Candidate raw data is populated exclusively from the requested manifest.
        if relative.parts[:2] == ("data", "raw"):
            continue
        source = root / relative
        target = staging / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def stage_corpus_expansion(manifest: Path, destination: Path, *, config: Path | None = None,
                           package_root: Path = ROOT) -> dict:
    package_root = Path(package_root).resolve()
    supplied_manifest = _absolute_unresolved(Path(manifest))
    if _symlink_component(supplied_manifest):
        raise ValueError("Manifest path has a symlink ancestor")
    manifest_path = supplied_manifest.resolve()
    destination = _absolute_unresolved(Path(destination))
    if _symlink_component(destination):
        raise ValueError("Destination path has a symlink ancestor")
    destination_resolved = destination.resolve()
    if destination.exists() or destination.is_symlink():
        raise ValueError(f"Destination already exists: {destination}")
    if _overlaps(destination_resolved, package_root):
        raise ValueError("Destination may not overlap the active package")
    if _overlaps(destination_resolved, manifest_path.parent):
        raise ValueError("Destination overlaps the source manifest directory")

    supplied_config = (_absolute_unresolved(Path(config)) if config
                       else package_root / "configs/app.json")
    if _symlink_component(supplied_config):
        raise ValueError("Config path has a symlink ancestor")
    config_path = supplied_config.resolve()
    if not config_path.is_file():
        raise ValueError("Config must be a regular, non-symlink file")
    cfg = read_json(config_path)
    requested_manifest, raw_by_id, copied_sources, corpus_id = _validated_inputs(manifest_path, cfg)

    files = package_files(package_root)
    baseline_hashes = {str(relative): digest((package_root / relative).read_bytes())
                       for relative in files}
    baseline_runtime_code_id = _runtime_code_id(package_root)
    for source_id, raw in raw_by_id.items():
        collision = package_root / "data/raw" / f"{source_id}.json"
        if collision.exists() and (collision.is_symlink() or collision.read_bytes() != raw):
            raise ValueError(f"Candidate raw-file collision: {source_id}")

    candidate_manifest = copy.deepcopy(requested_manifest)
    for source in candidate_manifest["sources"]:
        if source["status"] == "included":
            source["raw_file"] = f"raw/{source['source_id']}.json"
    candidate_config = copy.deepcopy(cfg)
    candidate_config["selection_status"] = "UNSELECTED_FOR_EXPANDED_CORPUS"
    candidate_config["generation_selection_status"] = "UNSELECTED_FOR_EXPANDED_CORPUS"
    candidate_config.pop("generation_selection_artifact", None)
    candidate_config["question_bank"] = QUESTION_BANK

    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = destination.parent / f".{destination.name}.staging-{uuid.uuid4().hex}"
    try:
        staging.mkdir()
        _copy_package(package_root, staging, files)
        write_json(staging / "data/manifest.json", candidate_manifest)
        write_json(staging / "configs/app.json", candidate_config)
        for source_id, raw in raw_by_id.items():
            target = staging / "data/raw" / f"{source_id}.json"
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                if target.read_bytes() != raw:
                    raise ValueError(f"Candidate raw-file collision: {source_id}")
            else:
                target.write_bytes(raw)

        candidate_rows, _, on_disk_manifest = prepare(
            manifest_path=staging / "data/manifest.json", cfg=candidate_config
        )
        on_disk_config = read_json(staging / "configs/app.json")
        if on_disk_config != candidate_config:
            raise ValueError("Candidate config changed during staging")
        if digest(candidate_rows) != corpus_id:
            raise ValueError("Candidate corpus identity changed during staging")
        candidate_runtime_code_id = _runtime_code_id(staging)
        if candidate_runtime_code_id != baseline_runtime_code_id:
            raise ValueError("Runtime code identity changed during staging")
        if (staging / QUESTION_BANK).exists():
            raise ValueError("A stale expansion question bank already exists")
        if baseline_hashes != {str(relative): digest((package_root / relative).read_bytes())
                               for relative in files}:
            raise ValueError("The active package changed during staging")

        receipt = {
            "status": "STAGED_VALIDATED_NOT_EVALUATED",
            "created_at": utc_now(),
            "baseline_root": str(package_root),
            "baseline_file_hashes": baseline_hashes,
            "baseline_runtime_code_id": baseline_runtime_code_id,
            "requested_manifest": str(manifest_path),
            "requested_manifest_hash": digest(requested_manifest),
            "requested_config": str(config_path),
            "requested_config_hash": digest(cfg),
            "candidate_config_hash": digest(on_disk_config),
            "candidate_manifest_hash": digest(on_disk_manifest),
            "candidate_corpus_id": digest(candidate_rows),
            "candidate_runtime_code_id": candidate_runtime_code_id,
            "copied_sources": copied_sources,
            "question_bank_status": "MISSING_PENDING_REVIEWED_EXPANSION_REFERENCES",
            "historical_reports_status": "COPIED_AS_HISTORICAL_ONLY",
            "generation_performed": False,
            "quality_evaluation_performed": False,
            "promotion_performed": False,
        }
        write_json(staging / RECEIPT_PATH, receipt)
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
    parser.add_argument("--destination", required=True, type=Path)
    parser.add_argument("--config", type=Path)
    args = parser.parse_args()
    receipt = stage_corpus_expansion(args.manifest, args.destination, config=args.config)
    print(json.dumps(receipt, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
