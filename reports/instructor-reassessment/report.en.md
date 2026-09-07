# Instructor-style reassessment and completed fixes

Assessment date: 2026-09-06. Scope: the **current local working tree**, including
uncommitted work, not the older GitHub commit. This is an independent-style
self-review against the [official rubric](https://github.com/DataTalksClub/llm-zoomcamp/blob/main/project.md#evaluation-criteria),
not an instructor-awarded grade. Existing changes were preserved; no commit,
publication or submission occurred.

**Conservative estimate: 14/26.** Core: **13/18**; named practices: **1/3**;
cloud/discretionary bonuses: **0/5**. A further RRF point is arguable but not included.
The five missing core points remain live retrieval-plus-LLM proof (2), actual
output comparison/selection (2), and complete reproducibility evidence (1).

This reassessment found and fixed additional evidence-integrity defects and verified
the current preview flow in a real browser. That increases confidence in the
implementation; it does not turn unexecuted generation into successful evidence.

## Criterion-by-criterion assessment

| ID | Criterion | Estimate / maximum | Evidence and instructor-style finding | What establishes full credit |
|---|---|---:|---|---|
| R01 | Problem description | 2/2 | README explains a researcher, literature questions, source-grounded comparisons and pending tag proposals, with scope limitations. | Preserve the clear scope. A real input-to-answer walkthrough would strengthen the presentation; it is not yet available. |
| R02 | Retrieval flow | 0/2 | The knowledge base works. The shared LLM route exists, but the actual browser LLM request failed because the selected course model is absent. No generated answer was observed. | Show a real answer using retrieved passages, sources and the same saved answer ID. The rubric's one-point tier is an LLM-only flow; I do not invent a KB-only partial tier. |
| R03 | Retrieval evaluation | 2/2 | Multiple approaches were actually evaluated and the development winner is active: vector, title+content, 750/150 windows. The new heading comparison did not justify replacing it. | Already supported for the criterion. Quality is still weak on some slices; a low metric is not an additional official deduction threshold. |
| R04 | LLM evaluation | 0/2 | Planning, frozen contexts, review schemas and a selector are implemented; actual paired answers and an evidence-selected generator are absent. | Run multiple approaches on the same questions/evidence, review results and make the selected settings active. Two prompts can satisfy the multiple-approach criterion; two models are our stronger experiment, not a course mandate. |
| R05 | Interface | 2/2 | The current Streamlit app was exercised in an actual browser: question, passages, expanded source, CSV download, feedback and missing-model error. | Preserve this evidence and add the live generated-answer path after setup. AppTest alone is not a browser test. |
| R06 | Ingestion pipeline | 2/2 | A fresh isolated dlt/DuckDB ingestion produced 377 verified windows from three snapshots; repeated ingestion is covered by existing integration tests. | Keep the exact export-to-index connection and repeat-load evidence. Tables remain explicitly excluded, not silently counted as indexed evidence. |
| R07 | Monitoring | 2/2 | QA feedback was saved for the correct answer and five real charts rendered. User-only scope was empty; QA scope showed the actual test activity. | Keep truthful origins and denominators. This demonstrates collection/dashboard capability, not researcher satisfaction. |
| R08 | Containerization | 2/2 | Full Compose wiring includes application, database, ingestion, local LLMs and encoder initialization. | This score follows the rubric's artifact wording. Build/start/restart remains unverified and is separately required for our release acceptance; do not call the stack tested. |
| R09 | Reproducibility | 1/2 | Versions, source data, instructions and offline encoder setup exist. Full local-model/database/container reproduction has not succeeded here. | One clean end-to-end rehearsal from the documented setup, with model identities, storage/restart and failure recovery. This is a provisional assessment of incomplete demonstrated setup, not proof that the code necessarily fails elsewhere. |
| R10 | Hybrid search | 1/1 | Text/vector fusion was actually evaluated with retained branch/rank evidence. It need not be the runtime winner for the explicit hybrid-evaluation allowance. | Already supported; do not force a worse hybrid default to display another technology. |
| R11 | Document reranking | 0/1 reserved | The course teaches manual RRF as reranking and it is implemented/evaluated. The current runtime uses vector retrieval, and the same fusion supplies the hybrid claim. | Present exact traces and seek the grader's interpretation of use/overlap. I do not require an untaught separate reranker, but I do not guarantee double credit. |
| R12 | Query rewriting | 0/1 | Bounded rewriting and fallback tests exist; rewriting is disabled and has no actual local-model experiment. | Show intent-preserving reformulations, before/after retrieval and harm cases, then justify runtime activation or rejection. Implemented code is not demonstrated benefit. |
| R13 | Cloud deployment | 0/2 | No cloud deployment exists. A private GitHub repository and local app are not cloud execution. | Real accessible deployment and operational evidence, within an explicitly approved feasible path. No free full-stack route is currently verified. |
| R14 | Discretionary additions | 0/3 | Source-preserving exports, pending proposals and provenance checks are useful, but measured research utility and a live complete product are not established. | Demonstrate an original useful addition and its working evidence. The actual reviewer decides whether and how many points to award. |

The core sum is `2+0+2+0+2+2+2+2+1 = 13`; named practices add 1. Peer-review
points are separate from this 26-point project rubric. Repository visibility was
rechecked and remains **PRIVATE** by owner choice. A public exact-commit review
release and actual cohort eligibility/submission are separate unresolved gates.

## What this review discovered and fixed

### 1. Export integrity could be bypassed by a malformed persisted record

**Reproduced:** an empty quotation passed substring membership, and a preview
record populated with claim fields could export a generated-looking claim row.
The application generation validator was stricter than its export boundary.
The [pre-fix probes](reproduced-gaps.json) explicitly record synthetic counterexamples.

**Fixed:** claim exports now reuse the strict answer validator, reject preview/
fixture modes with claims, reject empty/whitespace/non-string quotes, and enforce
status/claim consistency. Passage and derived claim exports now include source
license and language. The actual downloaded passage CSV was checked against all
five stored windows, including source hashes and licenses.

**Trade-off:** malformed legacy records now fail explicitly rather than produce
apparently valid exports. No historical source or stored record was rewritten.
This is source-integrity engineering around the taught flow, not a new biomedical
method or a claim that exact quotes establish semantic truth.

### 2. Selection trusted some labels more than their underlying evidence

**Reproduced:** changing a frozen reference requirement while retaining the same
question ID and claimed original bank hash could still produce a selection preview.
Record hashes alone did not establish that the evaluated requirement matched the
current question bank. Across model result files, a claimed identical context ID
also needed independent reconstruction from the actual inputs.

**Fixed:** the selector now compares complete frozen question records with the
current development bank; checks actual question, corpus, configuration and source
fields; recomputes the context identity; verifies filters/hit IDs; and checks the
generation request and raw response against the answer being reviewed. Every
nonempty context requires its own completed generation receipt. SDK-injected
fixtures are explicitly labeled and rejected as live selection evidence.

Calibration paths in selected evidence are repository-relative. At runtime,
changed calibration artifacts, fixtures or reviews invalidate the selection without
making another judge call. The new adversarial tests cover changed references,
questions, sources, context IDs, settings, requests, raw outputs, fixture labels,
missing calls and changed calibration input.

**Trade-off:** old incomplete evidence artifacts must be regenerated before use
as selection proof. No valid selected live release currently exists to migrate.
These checks catch inconsistent/accidentally altered evidence; hashes are not
cryptographic proof against someone deliberately rewriting every file and hash.
Synthetic unit fixtures remain identified as fixtures and do not establish quality.

### 3. Browser evidence now corresponds to the current implementation

The [browser receipt](browser-check.json) records:

- An actual preview search for the README's Italian-study limitations question.
- The relevant limitations passage at rank 5, expanded with its source coordinates.
- An actual five-row [downloaded CSV](downloaded-passages.csv), verified against
  the stored evidence rather than merely inspecting the server's export function.
- QA feedback for the preview answer; repeated submission did not duplicate it.
- Five rendered charts with one QA request and one rating initially. After the
  missing-model test, storage contained two requests, one rating and no model calls.
- A real LLM-mode error with no fabricated answer, followed by a reload that cleared
  session answer state while retaining the journal.

The download-control call stalled; the completed file was subsequently located in
Downloads and verified directly. Screenshots were inspected in tool output; no
saved screenshot file is claimed. The temporary server and tab were closed. Its
isolated QA database is excluded from the Docker build context; compact evidence
receipts remain available.

## Quality weaknesses that remain beyond the scoring checklist

The selected retriever has Hit@5 **21/35**, mean reference coverage **0.5667**, and
full reference coverage for **18/35** answerable development questions. In the
comparison slice, **0/7** are fully covered. A first relevant hit therefore does
not establish enough evidence for the promised comparison task.

The six heading ablations retained the incumbent because slice gains came with
exact-identifier/paraphrase regressions. Do not rerun parameter sweeps until a
preferred winner appears. First diagnose each missed requirement as absent source,
excluded material, incomplete label, missing candidate or low ranking. Preserve
all candidate/label changes and compare on development data only.

Three clinical seed papers do not establish comprehensive PHOX2B molecular coverage.
The review/guideline cannot be presented as original experimental evidence for
studies they cite. Unknown population/model metadata and excluded tables remain
visible. Literal quote-term proposals are review aids, not validated scientific tags.
Agent labels and judges are provisional; human scientific validation is neither
claimed nor invented as a mandatory course grading condition.

## Highest-value next actions and why

1. **Approved course-model setup and a small live pilot.** Current read-only model
   inventory contains Gemma 3 12B only; Phi3/Gemma 2B are absent and Docker is not
   installed. A pilot tests actual JSON behavior, context fit and latency before
   committing to a larger run. No model substitution or download was performed.
2. **Complete paired output evaluation and selection.** The full chosen matrix is
   two models/two prompts. A lower-setup first milestone is one taught model with
   two prompts and explicit agent reviews; the existing `evaluate-answers` and
   `select-generation` path supports it. This is enough to compare approaches for
   R04, without pretending the second-model experiment has happened. Preserve raw
   outputs, support/completeness/abstention judgments, failures and actual call counts.
3. **Verify the selected application and reserved final split.** The app must use
   the exact selected model/prompt/configuration and sources. Failed cases need
   reference-context diagnosis. The 18 final questions must not choose settings;
   exposed reruns become regression evidence.
4. **Complete reproduction and live browser delivery.** Save a real generated
   answer, sources, exports, feedback and database identity. Build/start the isolated
   Compose stack, retain state across restart, and test controlled model/database
   failure and recovery. This is the remaining route to the five core points.
5. **Only then pursue justified practices/extras.** Rewriting needs an intent/quality
   experiment; RRF overlap needs transparent grader interpretation; cloud needs
   an approved feasible deployment. Extra tables or more tests alone do not earn
   discretionary points automatically.

The [17 decision cards](../../docs/decisions.md) preserve the alternatives,
trade-offs, implementation contracts and revisit conditions. No new algorithm,
dependency or paid provider was added in this reassessment.

## Verification and evidence limits

**90 distinct local tests passed, zero skipped.** Four new tests include a
nine-mutation selection challenge. Imported test classes were removed from test
discovery to avoid inflating the count with duplicate execution. Existing real
dlt/DuckDB, cached encoder, minsearch and AppTest checks passed; model SDK and
PostgreSQL adapter fixtures are still not live-service evidence.

[Delivery checks](delivery.json) bind the code/configuration, source preservation,
test output and browser evidence. [Runtime preflight](runtime-preflight.json) is a
read-only installed-model inventory, not a generation run. No paid call, model
download, package installation, PostgreSQL migration, commit, push, public release
or submission occurred.

Earlier reviews cite IRB Copilot (24) and Civil Liberties Knowledge Assistant (25)
as comparison examples. This turn's attempt to reopen their official score pages
failed in the web tool; those values remain earlier recorded observations, not a
fresh verification. Public totals do not supply per-criterion reviewer reasons,
and the exact submitted versions were not established. They cannot justify a claim
that copying a particular stack will reproduce their grades.

The official rubric was re-read in this turn. General-repository logistics contain
historical links; actual cohort deadlines, access, reuse eligibility and peer-review
completion must be verified at submission time. **14/26 is a conservative current
working-tree estimate, not a promised final or official score.**
