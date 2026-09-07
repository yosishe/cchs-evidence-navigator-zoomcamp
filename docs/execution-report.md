> **Historical record.** This document describes its earlier runtime and approval state. For the submission candidate, use [current release evidence](release-status.md), [D37](release-decisions.md#d37--submission-candidate-with-an-explicit-quality-exception) and [setup](setup.md). Earlier pending items are not current-state assertions.

# Execution record

Core follow-up: the shared request flow, frozen paired contexts, six-slice pilots,
selected-only final evaluation, calibration binding, per-question/slice summaries,
generation selection and durable real-client attempt checkpoints were implemented.
[79 tests passed, zero skips](../reports/core-completion/checks-final.json).

The real local preflight was repeated outside the network sandbox and returned
`BLOCKED_MODEL_PREFLIGHT`, exit code 1, zero provider attempts. Only the existing
Gemma 3 model was available; it was not substituted for the course candidates.
The requested installation approval is pending. Live generation, answer quality,
PostgreSQL and Compose proof remain uncompleted; no new core points are claimed.
[Preflight evidence](../reports/core-completion/model-preflight.json).

The active remediation is documented in [review-remediation-v2.md](review-remediation-v2.md).
It implements the approved local, no-paid-provider, course-grounded plan while
preserving the original source publications and earlier experiment artifacts.

Executed: source-anchored 60-question bank validation, real representation/retrieval
experiments, repeated dlt/DuckDB ingestion, automated tests, independent ranking
contracts, browser preview and downloaded CSV verification, and read-only registry
manifest checks. Per-action files and remaining limitations are linked in the
remediation report. The final generation/test release was not run.

Not executed: installation of Docker or the two taught models, live local answer
comparison, automatic-judge calibration, rewrite quality evaluation, complete
PostgreSQL/Compose startup and restart, expert review, public release, commit/push,
cloud deployment or submission. Model commands performed preflight and recorded
missing models; they did not substitute the installed untaught model.

Historical reports describe the earlier 411-window/13-question configuration.
They are historical evidence, not results for the current 377-window/60-question
configuration. Do not carry their metrics or provisional score forward unchanged.


## Instructor reassessment — 2026-09-06

Current evidence: [full assessment](../reports/instructor-reassessment/report.en.md),
[real browser check](../reports/instructor-reassessment/browser-check.json),
[delivery verification](../reports/instructor-reassessment/delivery.json).
Ninety distinct local tests passed with no skips. Export validation and selection
input/receipt binding were strengthened after reproduced counterexamples. Preview,
source CSV, QA feedback, five charts, session reload and missing-model failure were
checked in the actual browser. No local model generated an answer. The temporary
server/tab were closed and isolated QA storage retained. No installation, migration,
commit, push, publication or submission occurred.

## Latest follow-up — Claude remediation rationale

Read both supplied Claude attachments, preserved their hashes, and implemented
JSON object requests, read-only runtime diagnostics, timeout fingerprinting,
session-origin dashboard defaults and complete accounting of schema-invalid model
outputs. Simplified the core evaluation/setup path to one Phi3 model and two
prompts with explicit assistant review. The optional two-model/judge route remains.

Ran 35 actual offline retrieval diagnostics against the frozen answerable
reference bank: 16 reference entries at ranks 6–20 and 15 outside the candidate
pool. No retrieval promotion, source edit or held-out evaluation occurred. See
[response and trade-offs](../reports/claude-remediation/response.en.md),
[raw diagnoses](../reports/claude-remediation/retrieval-misses.json),
[current checks](../reports/checks.json) and
[delivery verification](../reports/claude-remediation/delivery.json).
