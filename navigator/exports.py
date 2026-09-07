"""Research-table adaptations of the course's source metadata and pandas exports."""
from .common import csv_safe, verify_answer_style


def passage_rows(record):
    """One source window per row; never pretend previews contain generated claims."""
    fields = ("id", "source_id", "title", "section", "section_heading", "article_type", "year",
              "population_or_model", "source_url", "source_version", "passage_index",
              "start_in_passage", "end_in_passage", "bioc_offset", "license", "language")
    return [{"answer_id": record["id"], "question": record["question"],
             "corpus_id": record["corpus_id"], "config_id": record["config_id"],
             "mode": record["mode"], **{k: h.get(k) for k in fields},
             "exact_text": h["content"], "review_status": "PENDING_REVIEW"}
            for h in record["hits"]]


def claim_rows(record):
    # Revalidate persisted/legacy records at the export boundary. Python considers
    # the empty string a substring; substring membership alone is insufficient.
    from .rag import validate_answer
    verify_answer_style(record)
    if record["claims"] or record["status"] == "answered":
        if record["mode"] != "llm":
            raise ValueError("Preview or fixture records cannot export generated claims")
        validate_answer({key: record[key] for key in ("status", "claims", "limitations")}, record["hits"])
    lookup = {r["id"]: r for r in passage_rows(record)}
    rows = []
    for index, claim in enumerate(record["claims"], 1):
        if claim["evidence_id"] not in lookup:
            raise ValueError("Claim source is missing from the answer record")
        source = lookup[claim["evidence_id"]]
        if claim["exact_quote"] not in source["exact_text"]:
            raise ValueError("Claim quotation differs from the answer record")
        rows.append({**source, "claim_index": index, "claim_text": claim["text"],
                     **({"answer_style": record["answer_style"]} if "answer_style" in record else {}),
                     "claim_id": record["id"] + ":claim:" + str(index),
                     "answer_limitations": record.get("limitations", ""),
                     "support_review": record.get("support_review", "PENDING_REVIEW"),
                     "scientific_review": "PENDING_HUMAN_REVIEW",
                     "evidence_id": claim["evidence_id"], "exact_quote": claim["exact_quote"]})
    return rows


def comparison_rows(record):
    """Atomic claim rows grouped by the same question; no inferred agreement."""
    return [{**r, "comparison_id": record["id"],
             "comparison_status": "SOURCE_ROWS_ONLY_RELATION_NOT_ADJUDICATED"}
            for r in claim_rows(record)]


def tag_proposal_rows(record):
    """Quote-occurring term candidates, not synonyms, causal links or approved tags.

    This transparent extraction is an original adaptation of course metadata and
    tabular export patterns. Terms absent from the exact quote are never proposed.
    """
    import re
    vocabulary = ["PHOX2B", "PARMs", "NPARMs", "Hirschsprung", "neural crest",
                  "autonomic", "mosaicism", "penetrance", "genotype", "phenotype",
                  "hypercapnia", "hypoxia", "hypoventilation"]
    rows = []
    for claim in claim_rows(record):
        for term in vocabulary:
            match = re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", claim["exact_quote"], re.I)
            if match:
                rows.append({**claim, "proposal_id": claim["claim_id"] + ":term:" + term.lower(),
                    "proposed_term": match.group(0), "proposal_method": "quote_term_match_v1",
                    "proposal_reason": "This literal term occurs in the quoted evidence for this claim; review its research usefulness and relation to PHOX2B before use.",
                    "review_status": "PROPOSED_PENDING_HUMAN_REVIEW", "registry_action": "NONE"})
    return rows


def csv_export(rows):
    import pandas as pd
    return pd.DataFrame(rows).map(csv_safe).to_csv(index=False)
