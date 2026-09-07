# Architecture and data contracts

The core follow-up routes UI and evaluation through `rag.prepare_context` and
`rag.run_request`. Paired experiments acquire one immutable context per question
and reuse it across generators/prompts; the preparation ledger owns rewrite calls.
Reused preparation has no newly incurred retrieval time or provider attempt. Its
original timing and receipts remain linked in the result.

Generation selection records runtime Python-code identity, effective configuration,
corpus and hashes of development results/reviews. When generation status starts with SELECTED, the app and final-test path
verify selected evidence. The submission candidate deliberately retains a
non-SELECTED generation status under [D37](release-decisions.md#d37--submission-candidate-with-an-explicit-quality-exception);
its failed internal bar is disclosed, and final-test inference remains blocked. Evaluation reports accompany the container build so
these references remain available; runtime data and `.env` variants are excluded.

The [README](../README.md) contains the active flow diagram. Raw BioC snapshots are
normalized by original Python adapters, loaded through dlt into DuckDB, exported
and hash-checked before minsearch indexing. Headings remain `section_heading`
metadata; standalone headings, references, tables and figures do not become claims.

## Boundaries

- Source/window: `source_id`, source hash, passage index, exact character offsets,
  content, heading, article type, year, URL and license. Unknown population stays
  unknown. Schema changes produce a different corpus fingerprint.
- Retrieval: original query, optional rewrite, filters, both candidate ranks and
  fused ranks where applicable. RRF uses rank0; UI/MRR use rank1.
- Generation: provider (`ollama` by default), model, observed digest, prompt and
  context. Generated output owns only status/claims/limitations. Preview owns no
  generated claims. There is no local-to-paid fallback.
- Receipt: one per actual model API attempt, with stage, raw request/response,
  model/digest, status, latency and observed usage. Failed attempts remain visible.
- Review: result hash plus per-claim support and per-required-fact/qualification
  coverage. Schema validity, quote integrity and semantic support are distinct.
- Research export: atomic claim/source rows and literal quote-term proposals.
  Comparison relations remain unadjudicated and tags pending human review.
- Storage: PostgreSQL JSONB in the complete Compose path; explicit JSONL only for
  local development. The backend never silently substitutes after a DB failure.
  Existing payloads remain readable; legacy missing fields do not gain validation.
  New feedback must match its answer origin in both adapters; dashboard aggregation
  excludes and counts mismatches in every scope, including `all`.
- UI: one answer ID across result, exports and feedback. Sessions are isolated.
  QA/evaluation origins are kept separate from researcher activity and denominators.

## Packaging

Compose contains database, ingestion, Ollama, course-model initialization, encoder
initialization and application services. Encoder setup follows ingestion, shares
the explicit model cache, and validates inputs before the app starts. Serving uses
local encoder files only. Vectors remain in memory and rebuild per process. Startup waits for health and initializer completion; named volumes hold
weights, database and artifacts. Images are pinned by manifest digest. No host GPU
assumption is built into the portable CPU path. Historical Phi3 build, initialization, PostgreSQL restart and live browser
execution are recorded; two useful-answer calls timed out. The final Gemma route
is demonstrated natively with JSONL, not inside Compose. A database-outage
recovery drill remains distinct from successful restart persistence.

## Explicit limitations

An exact quote is not a semantic validator. A search hit is not a full answer.
Agent labels/judgments are not expert review. Table XML is preserved in sources but
not interpreted by this parser. The final native server allocated 4,096 tokens; architecture capacity does not
establish a larger active window. General overflow behavior is not proved. No infrastructure outside the taught
course boundary, paid endpoint or cloud deployment was added.
