"""Module 1 minsearch, Module 2 MiniLM, and homework zero-based RRF."""
from __future__ import annotations

from .common import digest, model_cache_dir, runtime_dir, write_json


class EncoderUnavailableError(RuntimeError):
    """Known setup failure safe to explain without revealing provider exceptions."""


def embedding_text(document, template):
    if template == "content":
        return document["content"]
    if template == "title_content":
        return document["title"] + "\n" + document["content"]
    if template == "title_heading_content":
        return "\n".join([document["title"], document.get("section_heading", "unknown"), document["content"]])
    raise ValueError("Unsupported embedding text template")


def reciprocal_rank_fusion(lists, k):
    if k <= 0:
        raise ValueError("RRF k must be positive")
    scores, lookup = {}, {}
    for ranking in lists:
        seen = set()
        for rank0, hit in enumerate(ranking):
            key = hit["id"]
            if key in seen:
                continue
            seen.add(key)
            scores[key] = scores.get(key, 0.0) + 1 / (k + rank0)
            lookup[key] = hit
    return [dict(lookup[key], score=scores[key])
            for key in sorted(scores, key=lambda key: (-scores[key], key))]


class Retriever:
    def __init__(self, documents, config):
        import minsearch

        self.documents, self.config = documents, config
        self.corpus_id = digest(documents)
        self.index = minsearch.Index(
            text_fields=config.get("lexical_fields", ["title", "section", "content"]),
            keyword_fields=["source_id", "article_type", "language"],
        ).fit(documents)
        self.model = self.vector_index = None

    def load_vectors(self, *, allow_download=False):
        import numpy as np
        from minsearch import VectorSearch
        from sentence_transformers import SentenceTransformer

        if self.vector_index is not None:
            return
        cfg = self.config
        try:
            self.model = SentenceTransformer(
                cfg["embedding_model"], revision=cfg.get("embedding_revision"),
                cache_folder=str(model_cache_dir()),
                device=cfg.get("embedding_device", "cpu"),
                local_files_only=not allow_download,
            )
        except OSError as exc:
            raise EncoderUnavailableError("Encoder unavailable in the configured cache. Run python -m navigator prepare-encoder; "
                                          "use --allow-download only after installation approval.") from exc
        template = cfg.get("embedding_text", "title_content")
        texts = [embedding_text(d, template) for d in self.documents]
        lengths = [len(self.model.tokenizer.encode(t, truncation=False)) for t in texts]
        matrix = np.asarray(self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False))
        if matrix.ndim != 2 or matrix.shape[0] != len(texts) or not np.isfinite(matrix).all():
            raise ValueError("Invalid embedding row/dimension contract")
        self.vector_index = VectorSearch(keyword_fields=["source_id", "article_type", "language"])
        self.vector_index.fit(matrix, self.documents)
        write_json(runtime_dir() / "embedding-report.json", {
            "model": cfg["embedding_model"], "requested_revision": cfg.get("embedding_revision"),
            "resolved_revision": getattr(self.model[0].auto_model.config, "_commit_hash", None),
            "corpus_id": self.corpus_id, "dimensions": matrix.shape[1],
            "normalization": "L2", "max_sequence_length": self.model.max_seq_length,
            "truncated_input_count": sum(n > self.model.max_seq_length for n in lengths),
            "input_count": len(texts),
            "device": str(self.model.device),
            "text_template": template,
            "allow_download": allow_download,
            "cache_directory": str(model_cache_dir()),
            "vectors_persisted": False,
        })


    def search(self, query, filters=None, method=None, top_k=None, *, trace=None):
        if not query.strip():
            return []
        filters = filters or {}
        if not set(filters) <= {"source_id", "article_type", "language"}:
            raise ValueError("Unsupported metadata filter")
        method = method or self.config["retrieval"]
        if method not in {"lexical", "vector", "hybrid"}:
            raise ValueError("Unsupported retrieval method")
        top_k = top_k or self.config["top_k"]
        if not 0 < top_k <= self.config["candidate_k"]:
            raise ValueError("Invalid search result count")
        n = self.config["candidate_k"] if method == "hybrid" else top_k
        if method in {"lexical", "hybrid"}:
            lexical = self.index.search(query, filter_dict=filters, boost_dict=self.config["boosts"], num_results=n)
        if method in {"vector", "hybrid"}:
            self.load_vectors()
            q = self.model.encode(query, normalize_embeddings=True)
            vector = self.vector_index.search(q, filter_dict=filters, num_results=n)
        if method == "lexical":
            hits = lexical
        elif method == "vector":
            hits = vector
        else:
            hits = reciprocal_rank_fusion([lexical, vector], self.config["rrf_k"])
        if trace is not None:
            trace.update(query=query, filters=dict(filters), method=method,
                candidate_k=n, final_k=top_k, rrf_k=self.config["rrf_k"],
                rank_convention="zero-based RRF; one-based displayed rank and MRR",
                lexical=[{"id": h["id"], "rank0": i} for i, h in enumerate(lexical)] if method in {"lexical", "hybrid"} else [],
                vector=[{"id": h["id"], "rank0": i} for i, h in enumerate(vector)] if method in {"vector", "hybrid"} else [],
                ranked=[{"id": h["id"], "rank": i, "score": h.get("score")} for i, h in enumerate(hits, 1)])
        # No invented lexical probability: minsearch documents may have no score.
        return [dict(h, rank=i, score=h.get("score")) for i, h in enumerate(hits[:top_k], 1)]


def prepare_encoder(*, allow_download=False):
    """Warm the pinned model cache and validate the corpus; serving stays offline.

    This does not persist a vector index: each app process builds its own in-memory
    index. Permission for a model download is an explicit operator prerequisite.
    """
    from .common import load_config, read_documents, read_json, utc_now, runtime_code_id
    started = utc_now()
    try:
        engine = Retriever(read_documents(), load_config())
        engine.load_vectors(allow_download=allow_download)
        report = {"status": "ENCODER_READY", "started_at": started,
                  "completed_at": utc_now(), "runtime_code_id": runtime_code_id(),
                  "embedding": read_json(runtime_dir() / "embedding-report.json")}
    except (OSError, RuntimeError, ValueError) as exc:
        report = {"status": "BLOCKED_ENCODER_SETUP", "started_at": started,
                  "error_type": type(exc).__name__, "allow_download": allow_download,
                  "next_step": "Check ingestion and the pinned encoder cache. Downloads require explicit approval."}
    write_json(runtime_dir() / "encoder-preparation.json", report)
    return report
