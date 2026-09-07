"""Independent exact-vector/identity and RRF audit; requires authorized local model setup."""
import resource
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from navigator.common import digest, load_config, read_documents, read_json, utc_now, write_json
from navigator.retrieval import Retriever

cfg, docs = load_config(), read_documents()
engine = Retriever(docs, cfg)
engine.load_vectors()
matrix = engine.vector_index.vectors
assert [d["id"] for d in engine.vector_index.docs] == [d["id"] for d in docs]
assert np.allclose(np.linalg.norm(matrix, axis=1), 1, atol=1e-5)
rows = []
for question in read_json(ROOT / load_config().get("question_bank", "data/evaluation/questions.json"))["questions"]:
    if question["split"] != "tuning":
        continue
    query_vector = engine.model.encode(question["question"], normalize_embeddings=True)
    scores = matrix @ query_vector
    order = np.argsort(-scores)
    expected = [docs[i]["id"] for i in order if scores[i] > 0][:cfg["candidate_k"]]
    actual = [h["id"] for h in engine.vector_index.search(query_vector, num_results=cfg["candidate_k"])]
    assert actual == expected, question["id"]
    rows.append({"question_id": question["id"], "top20_identity_matches": True,
                 "gold_vector_ranks": {gid: next(int(i)+1 for i, j in enumerate(order) if docs[j]["id"] == gid)
                                       for gid in question["relevant_ids"]}})

query = "Which organization performed the initial literature search for the guidelines?"
lexical = engine.search(query, method="lexical", top_k=cfg["candidate_k"])
vector = engine.search(query, method="vector", top_k=cfg["candidate_k"])
fused = engine.search(query, method="hybrid")
manual = {}
for ranking in [lexical, vector]:
    for rank0, hit in enumerate(ranking):
        manual[hit["id"]] = manual.get(hit["id"], 0) + 1 / (cfg["rrf_k"] + rank0)
assert [h["id"] for h in fused] == sorted(manual, key=lambda key: (-manual[key], key))[:cfg["top_k"]]
for hit in fused:
    assert abs(hit["score"] - manual[hit["id"]]) < 1e-12
filter_rows = []
for method in ["lexical", "vector", "hybrid"]:
    hits = engine.search(query, {"source_id": "PMC8039127"}, method=method)
    assert hits and all(h["source_id"] == "PMC8039127" for h in hits)
    near_collision = engine.search(query, {"source_id": "PMC80391270"}, method=method)
    assert near_collision == []
    filter_rows.append({"method": method, "restricted_source": "PMC8039127",
                        "ranked_ids": [h["id"] for h in hits], "near_collision_returns_empty": True})

report = {"created_at": utc_now(), "status": "PASS", "config_id": digest(cfg), "corpus_id": digest(docs),
          "scope": "Exact normalized NumPy ranking versus minsearch; row IDs, filters, and independently summed zero-based RRF. No configuration/label tuning.",
          "rows": len(docs), "dimensions": int(matrix.shape[1]), "all_row_ids_preserved": True,
          "per_question": rows, "filters": filter_rows,
          "fusion_example": {"query": query, "candidate_k": cfg["candidate_k"], "rrf_k": cfg["rrf_k"],
                             "lexical_ids": [h["id"] for h in lexical], "vector_ids": [h["id"] for h in vector],
                             "fused": [{"id": h["id"], "score": h["score"]} for h in fused]},
          "peak_process_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1 if sys.platform == "darwin" else 1024),
          "memory_scope": "Peak of this diagnostic process, including imports, model, documents, indexes and queries. Not isolated encoder memory or a deployment capacity benchmark.",
          "limitations": "No scientific label validation, approximate-search test, biomedical identifier precision estimate, live answer or PostgreSQL proof."}
write_json(ROOT / "reports/retrieval-contracts.json", report)
print({k: report[k] for k in ["status", "rows", "dimensions", "peak_process_rss_bytes", "config_id"]})
