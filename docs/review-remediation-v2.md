> **Historical record.** This document describes its earlier runtime and approval state. For the submission candidate, use [current release evidence](release-status.md), [D37](release-decisions.md#d37--submission-candidate-with-an-explicit-quality-exception) and [setup](setup.md). Earlier pending items are not current-state assertions.

# Evidence-focused remediation, 6 September 2026

## Core-points execution follow-up

Implemented: shared app/evaluation flow; frozen comparison contexts; six-slice
pilots and explicit IDs; selected-only final test; nonzero blocked/partial CLI
statuses; calibration binding; per-question/slice review; evidence-validated
generation selection; durable real-client attempt checkpoints.
[79-check result](../reports/core-completion/checks-final.json).

The live preflight still failed with zero generation attempts, now with exit 1.
Docker is absent. R02/R04/R09 remain open pending installation approval and actual
execution. [Preflight](../reports/core-completion/model-preflight.json) ·
[Delivery and preservation audit](../reports/core-completion/delivery.json).

No source article, question split, active retrieval parameter or model winner was
changed. No download, paid provider, final test, commit/push or publication occurred.
After approved setup, resume with the calibrated six-question pilot in the README;
inspect failures before the full comparison. Apply a winner only from completed
development evidence, then prove UI/PostgreSQL/Compose and final evaluation before
requesting a new grade.

This record supersedes the earlier remediation's active configuration. It does
not overwrite the historical examiner review or award a new grade. Implementation
is local and uncommitted; full execution is blocked pending installation approval.

## Implemented and measured

- Added local Ollama Chat Completions with course-backed Phi3/Gemma 2B candidates.
  Preview, generated output and paid execution are separate concepts. Unknown
  providers/models cannot silently substitute for the selected local model.
- Added actual call receipts (including failed attempts), raw input/output, model
  identity, stage and observed usage. Local API billing is zero; resource costs
  remain unmeasured. Commercial execution is disabled by default.
- Added mandatory fact and qualification coverage to answer review. Supported but
  incomplete answers fail. Legacy reviews without completeness cannot nominate a
  winner; neither can zero-success comparisons or held-out test results.
- Built 60 source-anchored assistant-authored questions: six slices, 42 development,
  18 held out. Existing 13-question evidence is preserved as exposed legacy data.
  All 13 exposed questions were rerun for retrieval regression across three methods,
  with explicit exact-quote remapping to current windows. They did not select the
  configuration, and their old test labels no longer mean an independent test.
- Compared three window sizes, both content representations and three retrieval
  methods after a browser-discovered heading defect. The selected 750/150,
  title+content, vector configuration has 377 windows, no encoder truncation,
  Hit@5 21/35, MRR@5 0.4695 and mean reference coverage 0.5667 on development data.
- Standalone headings are metadata rather than retrievable evidence. Seventy-eight
  such passages are excluded in addition to the earlier 312 exclusions. The raw
  publications are unchanged. Tables/figures remain explicitly outside retrieval.
- Manual RRF traces expose both candidate branches, zero-based ranks, fused scores
  and final ranks. The chosen runtime uses vector search; hybrid remains an
  evaluated alternative. No separate reranker is required by the rubric wording,
  and no double award is assumed.
- Implemented bounded rewriting, local paired-model/prompt runs, fictional judge
  calibration and reference-context diagnostics. Their live runs are **not done**.
- Added comparison rows and literal quote-based tag proposals. Proposals contain
  source identity, quotation, rationale and pending-human-review status, and never
  modify a research vocabulary. Semantic novelty and scientific benefit are not
  established by a term match.
- Added Ollama and model initialization to Compose. Python, PostgreSQL and Ollama
  image digests and ARM64 manifests were checked without downloading image layers.
- Disabled Streamlit's development file watcher in the documented and container
  launch commands. The first browser run worked but its backend watcher emitted
  optional Transformers image-module import errors. This compatibility adaptation
  avoids unrelated image dependencies; edits now require a server restart.

## Evidence index

| Evidence | What it proves |
|---|---|
| [Latest suite](../reports/checks.json) | Actual executed tests and explicit remaining external gates |
| [Legacy regression](../reports/remediation-v2/legacy-regression.json) | 39 real searches on the 13 exposed questions, with preserved originals and explicit quote remapping |
| [First nine comparisons](../reports/remediation-v2/retrieval-comparison.json) | Window experiment before identifying standalone headings |
| [Refined 18 comparisons](../reports/remediation-v2/retrieval-comparison-v2.json) | Same tuning questions, representations, all ranks, selection rule |
| [First/repeat final ingestion](../reports/remediation-v2/ingestion-final-first.json) / [repeat](../reports/remediation-v2/ingestion-final-repeat.json) | Actual dlt/DuckDB loads and matching corpus/file hashes |
| [Independent vector/RRF contracts](../reports/retrieval-contracts.json) | Exact ranking, row identities, filters and arithmetic on tuning queries |
| [Original browser finding](../reports/remediation-v2/browser-before-heading-fix.json) | Actual CSV download and a real retrieval defect; not fabricated success |
| [Final browser check](../reports/remediation-v2/browser-final.json) / [downloaded CSV](../reports/remediation-v2/browser-final-passages.csv) | Requested limitation paragraph at rank 5, no standalone headings, exact source fields and answer-linked QA feedback; preview only |
| [Coverage](../reports/remediation-v2/corpus-coverage.json) | Corpus roles, exclusion inventory and unresolved research gaps |
| [Model preflight](../reports/remediation-v2/local-matrix-preflight.json) | Requested taught models unavailable; zero generation requests |
| [Judge preflight](../reports/remediation-v2/judge-preflight.json) / [rewrite](../reports/remediation-v2/rewrite-preflight.json) | Blocked prerequisites, not quality results |
| [Container manifests](../reports/remediation-v2/container-image-manifests.json) | Registry identities/platforms, not a successful Docker build |
| [Preservation check](../reports/remediation-v2/source-preservation.json) | Nine protected project files unchanged and seven teaching files identical to the pinned Git objects; exact scope listed |
| [Delivery verification](../reports/remediation-v2/delivery-verification.json) | Final local checks, evidence boundaries and remaining execution gates |

## Decisions and limitations

Keep the task bounded to source comparison and reviewable proposals. Three
clinical publications can exercise this flow, but cannot substantiate systematic
CCHS coverage, molecular mechanism discovery or validated tag expansion. Reference
questions are authored by an assistant, may favor source language, and retain
label/relevance uncertainty. Adding independent primary PHOX2B research requires
an explicit task-coverage gap, access/license review and a new corpus/evaluation
version. No source was added merely to inflate document count.

The new tuning bank is harder and uses different questions from the legacy bank.
Do not compare its aggregate scores with the old 7-question scores as if this were
one controlled experiment. The before/after heading comparison uses the new bank
and is interpretable within that limited design. The final test remains unused.

The historical 17/26 was conditional. Reranking's earlier zero was an interpretation,
not proof that RRF is untaught; discretionary 0/3 was not three missing code tasks.
No new score is awarded until actual runtime and quality evidence supports it.

## Pending execution, in order

1. Obtain the requested authorization for Phi3/Gemma 2B downloads and Docker setup.
2. Verify installed model digests and input-context capacity; run a bounded pilot.
   Confirm that prompt/context are not silently truncated, on both models.
3. Run fictional judge calibration; inspect wrong-source, negation, omission and
   overgeneralization judgments. Failed calibration prevents quality acceptance.
4. Run two prompts on both models with fixed development contexts. Review answer
   support/completeness separately from schema/quote correctness. Record raw judge
   inputs/output and a separate agent audit, including shared-model judge bias.
5. Diagnose failed answerable cases with reference contexts, then evaluate bounded
   query rewriting and review intent preservation. Keep rejected variants visible.
6. Document the winning generation configuration, its digest and rejected choices;
   load that exact configuration. If no variant is adequate, report the limitation
   rather than promoting the least-bad one as a validated answer system.
7. Freeze configuration and run the final 18 questions once. Reopening tuning
   requires acknowledging test exposure and preparing a new final set.
8. Run the full Compose stack, live answer→storage→feedback→five charts, restart
   persistence and a clean-instructions rehearsal. Record native/container timing
   separately. No cloud deployment, public release, commit or submission is implied.
