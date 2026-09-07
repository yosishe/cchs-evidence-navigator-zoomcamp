"""Stable application configuration for mocked provider and evaluator tests.

These values describe synthetic unit-test transport. They intentionally do not
inherit the submitted application's selected model, prompt, or output schema.
"""
import copy


MOCK_CONFIG = {
    "retrieval": "vector",
    "top_k": 5,
    "candidate_k": 20,
    "rrf_k": 50,
    "boosts": {"title": 2.0, "section": 1.0, "content": 1.0},
    "model": "phi3",
    "prompt": "evidence_first",
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "embedding_revision": "1110a243fdf4706b3f48f1d95db1a4f5529b4d41",
    "max_output_tokens": 900,
    "chunk_chars": 750,
    "overlap_chars": 150,
    "selection_status": "SELECTED_ON_V2_PROVISIONAL_TUNING_LABELS",
    "embedding_text": "title_content",
    "embedding_device": "cpu",
    "provider": "ollama",
    "temperature": 0,
    "request_timeout_seconds": 120,
    "rewrite_enabled": False,
    "generation_selection_status": "CANDIDATE_NOT_QUALITY_SELECTED",
    "question_bank": "data/evaluation/questions-v2.json",
    "json_mode": True,
    "generation_json_schema": False,
}


def mock_config(**overrides):
    """Return an isolated complete config for a synthetic test scenario."""
    config = copy.deepcopy(MOCK_CONFIG)
    config.update(overrides)
    return config
