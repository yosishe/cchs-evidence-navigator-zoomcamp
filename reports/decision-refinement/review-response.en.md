# Grading-report response and decision improvements

Date: 2026-09-06. This is an implementation/evidence response, not an official
grade. The current decision authority is [docs/decisions.md](../../docs/decisions.md).

The attached `cchsevidencenavigatorgradingreport.en.md` was read as external review
material. Its SHA-256 is
`a910d9b247014b5afac8d4eace79f8d1c682eb4e166c97e053f97033ac4b08d2`;
the input path and pre-change project hashes are in [before.json](before.json).
Its recommendations are not owner approval for installation, publication or a
change to the course-only/no-payment constraints.

## Conclusion

The best next result comes from proving the core flow and improving evidence
coverage, while keeping the configuration consistent with measured outcomes.
More algorithms, charts or confident presentation cannot replace real generation,
paired output evaluation and complete reproduction. The attached report is right
about those missing proofs; some of its implementation findings describe an older
code snapshot, and several proposed shortcuts would weaken the evidence.

This refinement implements two operational corrections, runs a controlled search
experiment, expands all 17 implementation decision cards, clarifies the README,
and corrects the English handbook's artifact-specific RRF attribution. The active
retrieval/generation configuration and original source data are preserved. Live
generation and complete Compose acceptance remain open.

## Disposition of the attached recommendations

| Recommendation or claim | Decision and reason | Evidence / next verification |
|---|---|---|
| Prove a real model-backed answer and the whole UI flow | Accept; highest-priority missing proof. A successful fixture or preview is insufficient. | D07/D08; course-model setup remains unapproved/unavailable. Save answer ID across UI, exports, DB, feedback and dashboard after setup. |
| Evaluate multiple output approaches and load the winner | Accept. Shared contexts, agent reviews, calibration binding and selection manifests are implemented. | D11; actual generation comparison still pending. Two prompts already constitute multiple approaches in the rubric; two models are our stronger chosen experiment. |
| Judge calibration was not tied to evaluation | Addressed before this refinement. Calibration is bound to model digest, instructions/settings and fixture/review hashes. | `navigator/experiments.py`, `tests/test_core_completion.py`; passing fixtures is not scientific validation. |
| Evaluator and app might diverge | Addressed before this refinement through shared `run_request`/`prepare_context`. | Parity and frozen-context tests; live UI/model parity still needs demonstration. |
| Blocked commands could appear successful | Addressed before this refinement with explicit statuses and nonzero CLI exits. New encoder setup follows the same rule. | `navigator/__main__.py`; missing-cache receipt and CLI regression check. |
| First query might silently download the encoder | Accepted and fixed. Explicit preparation populates/checks the cache; normal retrieval uses local files only. Compose app depends on encoder initialization. | [Cached check](encoder-cached.json), [empty-cache check](encoder-empty-cache.json). Full container initialization unexecuted. |
| Add source quotas for comparisons | Experiment only. The earlier named-source probe helped some cases but harmed another. Source presence does not guarantee relevant evidence. | D05; prior seven-case diagnostic in the workspace's `comparison-probe.json`; no runtime promotion. Future routes must use user-visible source selection, never reference-label IDs. |
| Add headings to text/vector search | Tested in six controlled development variants. No candidate beats the selected vector's overall rule; retain incumbent. | [Heading ablation](heading-ablation.json), D04/D12; all per-case gains and regressions retained. |
| Tune lexical boosts / enlarge candidates | Potential follow-up after miss diagnosis, not a blanket improvement. Larger pools and different ranking are distinct interventions. | Predeclare a bounded development grid, retain identifiers/filters, hold final depth fixed and report context/latency plus quality. |
| Add an LLM or metadata reranker to obtain a separate point | Not adopted on this rationale. Answer judging does not establish that the same course taught an LLM reranker. Heading search is representation, not automatically reranking. | Optional course lesson explicitly demonstrates RRF; no invented requirement for an independent second algorithm or assumed double credit. |
| Loosen output rules / use a stronger installed model | Keep exact provenance/schema rules. Model size or installed availability does not establish permitted use or quality. | D08. Phi3/Gemma 2B remain candidates; Gemma 3 is outside the demonstrated-use evidence currently established. |
| Use JSON response mode / shorten prompt or context | Conditional pilot candidates, not measured fixes. JSON syntax cannot prove completeness or entailment; trimming can remove needed qualifications. | After real failure diagnosis, compare a single supported adapter/prompt change with equal evidence and preserved validation. No untested configuration change in this turn. |
| Cross-judge using both models | Optional disagreement diagnostic. It doubles judging calls, correlated judges can share errors, and agreement is not ground truth. | Keep calibrated judging plus explicitly identified agent inspection. Neither counts as biomedical expert review. |
| Add more charts / show QA in the default dashboard | A chart needs an operational question and denominator. Five required charts already exist. QA can be selected explicitly without changing its origin. | D14; preserve `user`, `qa`, `evaluation`, and `legacy_unknown`. No dummy user activity. |
| Mark an agent demonstration with `traffic_origin=user` | Reject mislabeling. The report's demonstration suggestion would pollute researcher-activity interpretation. | Storage now rejects origin mismatch; dashboard excludes/reports mismatches even under `all`. |
| Move all incomplete-status language out of the README opening | Keep material blockers visible in a concise capability/evidence table; reduce repetition rather than conceal facts. | Updated README links each current capability to remaining proof. A real answer screenshot remains pending. |
| Use past high-scoring projects to infer how to get points | Use documentation patterns as examples only. The report does not establish submitted-commit identities or public per-criterion reviewer reasons. | Its cited total scores are historical context, not causal evidence that a technology earns points. No new grade is inferred here. |
| Give a KB-only flow the rubric's one-point tier | Do not treat this as the official tier. The current one-point retrieval-flow wording refers to an LLM queried directly without a KB. | [Official rubric](https://github.com/DataTalksClub/llm-zoomcamp/blob/main/project.md#evaluation-criteria), checked again in this turn. Keep implementation inspection separate from executed-flow proof. |
| Deduct container points because it was never built | Lack of a run is a valid readiness concern. The R08 wording itself is about everything being in Compose; R09 additionally requires working reproduction. | Do not invent an intermediate official tier. Full clean rehearsal remains our required acceptance evidence. |
| Change the Ollama image because of its alleged age | No change based on an unverified date assertion. Existing manifest identity is recorded, but compatibility needs a real run. | D15; update only for an observed incompatibility or a verified relevant release change, then rerun evidence. |
| Deploy on a suggested free cloud VM | Deferred: no approved, demonstrated, free full-stack route has been verified. The report's proposed CPU/RAM/time values are unmeasured scenarios. | Local core gates first. No deployment or external account action performed. |
| Publish, commit, submit, use another attempt/cohort | Not authorized by a review attachment. Technical quality is separate from owner approval, eligibility, submission history and current logistics. | D17; recheck official platform at actual submission. No publication/commit/push/submission performed. |

The report's 63-test snapshot is superseded by [86 passing local checks](../checks.json),
including seven new tests in `tests/test_decision_refinement.py`. Increased test count
is not a claim of increased model accuracy or newly awarded points.

## Completed experiment: headings do not justify changing the default

**Hypothesis:** parent headings might identify limitations/comparison evidence more
clearly. **Design:** same 377 windows and IDs, 42 development questions, top-5, pinned
cached MiniLM, existing boosts and RRF settings. Run the three baselines and three
heading counterparts. Heading lexical/vector are individual branch changes; heading
hybrid combines both and is not an isolated reranker test. No final questions were
evaluated, no generation calls or downloads occurred, and the app config was not
promoted automatically.

| Variant | Hits / 35 answerable | MRR@5 | Mean reference coverage@5 | Fully covered / 35 |
|---|---:|---:|---:|---:|
| Lexical baseline | 14 | 0.2881 | 0.3524 | 11 |
| **Vector baseline — retained** | **21** | **0.4695** | **0.5667** | **18** |
| Hybrid baseline | 20 | 0.3452 | 0.4952 | 15 |
| Heading lexical | 12 | 0.2357 | 0.3286 | 11 |
| Heading vector | 21 | 0.4171 | 0.5619 | 18 |
| Heading hybrid | 20 | 0.4057 | 0.5095 | 16 |

All four vector-using variants had zero encoder truncation. The seven absent-evidence
questions retain rankings but have no fabricated retrieval reference denominator.

Heading vectors raised COM-05 coverage from 0 to 1/2, COM-06 from 2/3 to 1, and
LIM-02 from 0 to 1. They lowered PAR-06 and EXA-04 from 1 to 0. Thus a gain in the
intended slices did not improve overall reference coverage. The fixed selection
rule retains baseline vector. The active configuration remains unchanged, and
heading options are available only as explicit experimental parameters.

The ablation receipt preserves the code hash at execution. The final change after
that run only adds an actionable encoder-setup error in the UI and a dedicated
exception class; no ranking logic, corpus, labels or active settings changed.

This does not prove headings are always harmful: these are small, agent-labeled
development data. Single-run timings include cache/process-order effects and are
not statistically reliable performance comparisons. Further parameter sweeps would
increase development overfitting risk; inspect the failed references first.

## Verification performed and limits

- Python suite: **86 passed, zero skips**, including real existing dlt/DuckDB,
  minsearch/MiniLM and Streamlit AppTest integrations. Model SDK responses and the
  PostgreSQL origin check in tests use mocks; AppTest is not a browser.
- Six heading variants: **252 actual searches** on development questions. Four
  variants encode the corpus from the existing cache; no local LLM generation.
- Real offline encoder preparation: an empty temporary cache produces
  `BLOCKED_ENCODER_SETUP`; the existing project cache produces `ENCODER_READY`.
  The receipt explicitly says vectors are not persisted.
- New origin checks prevent mismatched QA/user feedback in storage and exclude
  historical mismatches from all-scope aggregates. They do not rewrite stored
  events, apply a migration, or prove a live PostgreSQL transaction.
- Delivery integrity and link checks are recorded in [delivery.json](delivery.json).
  Original data/configuration/locks are compared to the pre-change snapshot.

No live Phi3/Gemma answer, calibrated model judge, full generation selection,
final-test generation, Docker build, PostgreSQL restart or new browser walkthrough
was performed. The installation/setup approval request remains unanswered; this
turn did not repeat it or treat the attachment as consent. No packages/models were
installed, paid endpoint used, or source published.

## What closes the remaining five core points

| Order | Concrete deliverable | Why this comes first / acceptance evidence |
|---|---|---|
| 1 | Approved setup plus six-slice local pilot | Verify real schema, context fit, provenance and latency before a large run. A broken pilot triggers diagnosis, not fabricated successful rows. |
| 2 | Complete paired development outputs and reviews | Keep the same contexts, actual model digests, all failures, support/completeness/abstention judgments and call accounting. Choose and apply the evidence-supported configuration. |
| 3 | Selected-only final evaluation and error analysis | Use all reserved final questions; no model/prompt selection from this result. Report weak slices and failure causes. |
| 4 | Actual browser-to-storage demonstration | Same answer ID in generated output, exported JSON/CSV, feedback and monitoring. Keep demonstration origin `qa`. |
| 5 | Clean, isolated Compose rehearsal | Build, ingest, initialize both kinds of model, generate, save to PostgreSQL, restart without deleting volumes, verify persistence and controlled recovery. Save exact reproduction receipts. |

These address R02 (+2), R04 (+2) and the remaining R09 point under the earlier core
assessment. They are **future evidence gates**, not points earned by this report.
Optional rewriting/cloud/discretionary scores remain separate. A reviewer may
interpret practice overlap differently; no maximum grade is promised.
