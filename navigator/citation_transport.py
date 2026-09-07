"""Application-owned citation transport, adapted from course context composition.

Only whitespace can be normalized. No fuzzy matching, case folding, punctuation
repair or semantic certification. Original source bytes and source IDs stay owned
by the application. Receipts permit deterministic replay before selection.
"""
from __future__ import annotations

import re


def whitespace_map(text):
    chars, spans = [], []
    for match in re.finditer(r"\s+|\S", text):
        chars.append(" " if match.group().isspace() else match.group())
        spans.append(match.span())
    return "".join(chars), spans


def resolve_quote(raw_quote, hit):
    if not isinstance(raw_quote, str) or not raw_quote.strip():
        raise ValueError("Empty or non-string quotation")
    source = hit["content"]
    normalized, spans = whitespace_map(source)
    needle = whitespace_map(raw_quote)[0].strip()
    first = normalized.find(needle)
    if first < 0 or normalized.find(needle, first + 1) >= 0:
        raise ValueError("Quotation is absent or ambiguous within the specified passage")
    start, end = spans[first][0], spans[first + len(needle) - 1][1]
    quote = source[start:end]
    return quote, {"raw_quote": raw_quote, "canonical_quote": quote,
        "normalization": "exact" if raw_quote == quote else "whitespace_only",
        "start_in_chunk": start, "end_in_chunk": end,
        "start_in_passage": hit.get("start_in_passage", 0) + start,
        "end_in_passage": hit.get("start_in_passage", 0) + end,
        "evidence_id": hit["id"], "source_version": hit.get("source_version")}


def decode_numbered(payload, hits):
    if not isinstance(payload, dict) or set(payload) != {"status", "claims", "limitations"}:
        raise ValueError("Unexpected numbered answer fields")
    if not isinstance(payload["claims"], list):
        raise ValueError("Claims must be a list")
    claims, receipts = [], []
    for claim in payload["claims"]:
        if not isinstance(claim, dict) or set(claim) != {"text", "passage", "quote"}:
            raise ValueError("Unexpected numbered claim fields")
        number = claim["passage"]
        if type(number) is not int or not 1 <= number <= len(hits):
            raise ValueError("Passage number is not a request-local integer")
        hit = hits[number - 1]
        quote, receipt = resolve_quote(claim["quote"], hit)
        receipts.append({**receipt, "passage": number, "transport_version": 1})
        claims.append({"text": claim["text"], "evidence_id": hit["id"], "exact_quote": quote})
    return {"status": payload["status"], "claims": claims, "limitations": payload["limitations"]}, receipts


def source_spans(text):
    """Lossless display spans, not an NLP claim about sentence boundaries.

    The heuristic splits after sentence-like punctuation and whitespace. It
    preserves every character, decimal and fragment in the frozen source window.
    A pointer identifies a position even when the same wording occurs twice.
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Source spans require nonempty source text")
    boundaries = [0, *[m.end() for m in re.finditer(r'(?<=[.!?])\s+(?=[A-Z0-9(])', text)], len(text)]
    return [{"span": i, "start": start, "end": end, "text": text[start:end]}
            for i, (start, end) in enumerate(zip(boundaries, boundaries[1:]), 1)]


def _span_reference(reference, hits):
    fields = {"passage", "from_span", "to_span"}
    if (not isinstance(reference, dict) or set(reference) != fields
            or any(type(reference[k]) is not int for k in fields)):
        raise ValueError("Source references require three integer pointers")
    number, first, last = (reference[k] for k in ("passage", "from_span", "to_span"))
    if not 1 <= number <= len(hits):
        raise ValueError("Unknown passage pointer")
    hit = hits[number - 1]; spans = source_spans(hit["content"])
    if not 1 <= first <= last <= len(spans):
        raise ValueError("Unknown or reversed source span range")
    start, end = spans[first - 1]["start"], spans[last - 1]["end"]
    quote = hit["content"][start:end]
    receipt = {**reference, "transport_version": 2, "transport": "source_spans",
        "quote_origin": "application_source_span", "canonical_quote": quote,
        "start_in_chunk": start, "end_in_chunk": end,
        "start_in_passage": hit.get("start_in_passage", 0) + start,
        "end_in_passage": hit.get("start_in_passage", 0) + end,
        "evidence_id": hit["id"], "source_version": hit.get("source_version")}
    return hit, quote, receipt


def decode_source_spans(payload, hits):
    if (not isinstance(payload, dict) or set(payload) != {"status", "claims", "limitations"}
            or payload["status"] not in {"answered", "insufficient_evidence"}
            or not isinstance(payload["claims"], list) or not isinstance(payload["limitations"], list)):
        raise ValueError("Unexpected source-span answer fields")
    if payload["status"] == "insufficient_evidence":
        if payload["claims"] or payload["limitations"]:
            raise ValueError("Source-span abstention must not add claims or qualifications")
        return {"status": "insufficient_evidence", "claims": [],
                "limitations": "The supplied passages do not establish the information requested."}, []
    claims, qualifications, receipts = [], [], []
    for i, claim in enumerate(payload["claims"], 1):
        if not isinstance(claim, dict) or set(claim) != {"text", "passage", "from_span", "to_span"}:
            raise ValueError("Unexpected source-span claim fields")
        reference = {k:v for k,v in claim.items() if k != "text"}
        hit, quote, receipt = _span_reference(reference, hits)
        claims.append({"text": claim["text"], "evidence_id": hit["id"], "exact_quote": quote})
        receipts.append({**receipt, "target": "claim", "target_index": i})
    for i, reference in enumerate(payload["limitations"], 1):
        hit, quote, receipt = _span_reference(reference, hits)
        qualifications.append(f"{hit['source_id']}, passage {hit.get('passage_index', 'unknown')}: {quote}")
        receipts.append({**receipt, "target": "limitation", "target_index": i})
    return {"status": "answered", "claims": claims, "limitations": "\n".join(qualifications)}, receipts


def decode_source_extracts(payload, hits):
    """Model-selected excerpts, with no generated scientific paraphrase.

    Global span IDs address positions in the complete request context. The model
    still must select relevant, sufficient and appropriately qualified evidence.
    Literal output is not automatically a relevant or complete answer.
    """
    if (not isinstance(payload, dict) or set(payload) != {"status", "claims", "limitations"}
            or payload["status"] not in {"answered", "insufficient_evidence"}
            or not isinstance(payload["claims"], list) or not isinstance(payload["limitations"], list)):
        raise ValueError("Unexpected source-extract answer fields")
    if payload["status"] == "insufficient_evidence":
        if payload["claims"] or payload["limitations"]:
            raise ValueError("Extractive abstention must not attach claims or qualifications")
        return {"status": "insufficient_evidence", "claims": [],
                "limitations": "The supplied passages do not establish the information requested."}, []
    pointers = [{"passage": i, "from_span": span["span"], "to_span": span["span"]}
                for i, hit in enumerate(hits, 1) for span in source_spans(hit["content"])]
    claims, qualifications, receipts = [], [], []
    for target in ("claims", "limitations"):
        for index, choice in enumerate(payload[target], 1):
            if (not isinstance(choice, dict) or set(choice) != {"span"}
                    or type(choice["span"]) is not int or not 1 <= choice["span"] <= len(pointers)):
                raise ValueError("Unknown or model-modified global source span")
            hit, quote, receipt = _span_reference(pointers[choice["span"] - 1], hits)
            receipt.update(transport_version=3, transport="verbatim_span_selection",
                           global_span=choice["span"], target=target[:-1], target_index=index)
            if target == "claims":
                claims.append({"text": quote, "evidence_id": hit["id"], "exact_quote": quote})
                receipt["claim_text_origin"] = "application_source_verbatim"
            else:
                qualifications.append(f"{hit['source_id']}, passage {hit.get('passage_index', 'unknown')}: {quote}")
            receipts.append(receipt)
    return {"status": "answered", "claims": claims, "limitations": "\n".join(qualifications)}, receipts
