"""BioC adaptation of Module 1 chunking and the dlt filesystem workshop."""
from __future__ import annotations

import json
import time
from pathlib import Path

from .common import ROOT, digest, load_config, read_json, runtime_dir, utc_now, write_json

EXCLUDED_TYPES = {"REF", "REFERENCES", "TITLE", "AUTH_CONT", "COMP_INT", "ABBR",
                  "ACK_FUND", "SUPPL", "TABLE", "FIG"}


def windows(text, size, overlap):
    if not 0 <= overlap < size:
        raise ValueError("Chunk overlap must be nonnegative and smaller than size")
    for start in range(0, len(text), size - overlap):
        end = min(start + size, len(text))
        if text[start:end].strip():
            yield start, end, text[start:end]
        if end == len(text):
            break


def normalize_source(source, raw, cfg):
    if digest(raw) != source["sha256"]:
        raise ValueError(f"Source hash mismatch: {source['source_id']}")
    obj = json.loads(raw)
    collections = obj if isinstance(obj, list) else [obj]
    documents = [d for c in collections for d in c.get("documents", [])]
    if len(documents) != 1 or documents[0]["id"] != source["source_id"]:
        raise ValueError("Unexpected BioC publication identity")
    rows, exclusions = [], []
    heading = "unknown"
    for index, passage in enumerate(documents[0].get("passages", [])):
        infons = passage.get("infons", {})
        section = infons.get("section_type", "UNKNOWN").upper()
        kind = infons.get("type", "").lower()
        text = passage.get("text", "")
        if kind.startswith("title"):
            heading = text.strip() or heading
            exclusions.append({"source_id": source["source_id"], "passage_index": index,
                               "section": section, "reason": "heading_retained_as_metadata_only"})
            continue
        if section in EXCLUDED_TYPES or kind in {"ref", "front", "table", "table_caption", "fig_caption"} or not text.strip():
            exclusions.append({"source_id": source["source_id"], "passage_index": index,
                               "section": section, "reason": "non_evidence_type_or_empty"})
            continue
        for start, end, content in windows(text, cfg["chunk_chars"], cfg["overlap_chars"]):
            identity = f"{source['source_id']}:{source['sha256'][:16]}:{index}:{start}:{end}"
            rows.append({
                "id": identity, "source_id": source["source_id"],
                "source_version": source["sha256"], "passage_index": index,
                "start_in_passage": start, "end_in_passage": end,
                "bioc_offset": passage.get("offset", 0), "content": content,
                "title": source["title"], "section": section,
                "section_heading": heading,
                "year": str(source.get("year", "unknown")),
                "article_type": source.get("article_type", "unknown"),
                "population_or_model": "unknown", "language": "en",
                "source_url": source["article_url"], "license": source["license"],
            })
    return rows, exclusions


def prepare(manifest_path=None, cfg=None):
    cfg = cfg or load_config()
    manifest_path = manifest_path or ROOT / "data/manifest.json"
    manifest = read_json(manifest_path)
    rows, excluded = [], []
    for source in manifest["sources"]:
        if source["status"] != "included":
            continue
        raw = (manifest_path.parent / source["raw_file"]).read_bytes()
        new_rows, new_excluded = normalize_source(source, raw, cfg)
        rows.extend(new_rows)
        excluded.extend(new_excluded)
    if not rows or len({r["id"] for r in rows}) != len(rows):
        raise ValueError("No evidence or duplicate chunk IDs; ingestion stopped")
    return sorted(rows, key=lambda r: r["id"]), excluded, manifest


def ingest():
    """Replacement is scoped to this application's reproducible ingestion table."""
    import dlt

    start = time.perf_counter()
    rows, excluded, manifest = prepare()
    runtime = runtime_dir()
    runtime.mkdir(parents=True, exist_ok=True)
    resource = dlt.resource(rows, name="passages", primary_key="id")
    pipeline = dlt.pipeline(
        pipeline_name="cchs_evidence",
        pipelines_dir=str(runtime / "dlt"),
        destination=dlt.destinations.duckdb(credentials=str(runtime / "ingestion.duckdb")),
        dataset_name="evidence",
    )
    load = pipeline.run(resource, write_disposition="replace")
    fields = list(rows[0])
    with pipeline.sql_client() as client:
        with client.execute_query("SELECT " + ", ".join(fields) + " FROM passages ORDER BY id") as cur:
            exported = [dict(zip(fields, row)) for row in cur.fetchall()]
    if digest(exported) != digest(rows):
        raise ValueError("DuckDB export does not match prepared index input")
    target = runtime / "documents.jsonl"
    tmp = target.with_suffix(".tmp")
    tmp.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in exported))
    tmp.replace(target)
    report = {
        "status": "EXECUTED", "created_at": utc_now(), "engine": "dlt/duckdb",
        "source_count": len({r["source_id"] for r in rows}), "chunk_count": len(rows),
        "excluded_passage_count": len(excluded), "corpus_id": digest(rows),
        "manifest_hash": digest(manifest), "documents_sha256": digest(target.read_bytes()),
        "seconds": time.perf_counter() - start, "load_ids": list(load.loads_ids),
        "config": {k: load_config()[k] for k in ["chunk_chars", "overlap_chars"]},
    }
    write_json(runtime / "ingestion-report.json", report)
    write_json(runtime / "exclusions.json", excluded)
    return report


def verify_quote(hit, quote):
    return isinstance(quote, str) and bool(quote.strip()) and quote in hit["content"]
