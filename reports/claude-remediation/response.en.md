# Response to Claude's remediation rationale

The notes identify the right priority: demonstrate the knowledge-base-to-model
flow, compare real answers and make reproduction reviewable. This update fixes
additional software and evaluation weaknesses and simplifies the completion route.
It does **not** establish the five missing core points or a passing grade.

Inputs: both user-supplied Claude documents were read, including all 366 lines of
the new rationale. Their hashes and the starting working tree are preserved in
[before.json](before.json). The missing companion “remediation plan” linked inside
Claude's rationale was not supplied; its contents are not assumed. Prior findings
are addressed in the [earlier response](../decision-refinement/review-response.en.md)
and [instructor reassessment](../instructor-reassessment/report.en.md).

## Changes implemented

| Change | Why / alternative / trade-off | Verification |
|---|---|---|
| One Phi3 model, two prompts as the first completion route | Multiple prompts can meet the multiple-approaches criterion. Starting with two models and two judges adds setup and review work without being required. This route cannot claim a model-family comparison. | [Pilot plan](pilot-plan.json): at most 12 calls; [full development plan](development-plan.json): at most 84. No calls executed by planning. |
| JSON object response mode in the existing Ollama SDK call | Preserve strict schema and verbatim-quote validation. Avoid permissive parsing or hand-corrected outputs. Syntax support is not semantic support and its actual benefit remains unmeasured. | SDK-argument/receipt tests, including explicit mode-off candidate; existing rejection tests still pass. |
| Completed malformed answers remain evaluation failures | Stopping at the first malformed answer prevented a complete paired comparison. Retain the output, count it as an error/unacceptable answer, review it and continue without retry. Service/preflight failures still stop. | Malformed-first/valid-second fixture, service-outage fixture, and selector test rejecting a fabricated failure. |
| Bounded timeout override with configuration identity | Native and CPU-container timing may differ. Permit a positive finite override; reject NaN/infinity/nonpositive values. Preserve hashes for numerically equivalent settings; changed settings invalidate old selection. | Override/value/hash tests and receipt assertions. No unmeasured p95-based value adopted. |
| Read-only runtime diagnostics | Record real CLI/server versions, model digests, quantization and available context metadata. A model's architecture capacity is not its loaded context window. Never pull or generate during preflight. | [Actual preflight](runtime-preflight.json), missing-model exit test, metadata fixtures. |
| Dashboard defaults to the session origin | QA operators see their activity immediately while it remains labeled QA. Defaulting to mixed `all` would blur the initial interpretation. | Streamlit AppTest and current browser observation; origin-integrity tests retained. |
| Reference-miss diagnosis | Diagnose candidate absence separately from final ranking before selecting an improvement. Adding a reranker cannot recover an absent candidate. | [Raw diagnosis](retrieval-misses.json), [reviewable CSV](retrieval-misses.csv), 35 actual offline searches. |
| Clearer reviewer and operator route | Keep current limitations visible and put measured results, code and setup steps within direct reach. Remove unnecessary two-model/judge prerequisites from the active instructions. | README, execution prompt, decision cards and evaluation protocol updated together. |

## What the retrieval diagnosis establishes

The active vector configuration still obtains a known-reference hit on 21 of 35
answerable development questions; 18 have complete reference coverage. Of 67
reference entries, 36 are in the top five, 16 lie at ranks 6–20 and 15 are outside
the top 20. These entries are not independent passages/studies. Fourteen questions
have no reference hit; 17 have incomplete coverage.

The next ranking experiment can target the 16 lower-ranked entries. For the 15
absent candidates, first inspect query wording, representation and explicit source
filters. The earlier heading ablation already showed trade-offs and did not beat
the incumbent overall; repeating an unbounded search for a favorable metric is
not justified. All labels remain provisional; alternate relevant evidence may be
unlabeled. No source, quote, split, retrieval default or model selection was changed.

## Recommendations corrected or deferred

- **Already resolved before these notes:** shared app/evaluator flow, frozen
  contexts, nonzero blocked CLI exits, feedback-origin equality, explicit offline
  encoder preparation, stronger selection provenance and CSV quote integrity.
- **Context guard:** do not treat characters divided by three or a prompt count
  near a window boundary as proof of truncation. Metadata diagnosis is now
  implemented; a measured model-specific capacity/retention experiment is still
  needed. No server context value was changed based on a guessed default.
- **Model details:** `/api/show` is a read-only **POST**, not the proposed GET.
  Architecture capacity and `/api/ps` loaded context are recorded separately.
- **Version mismatch:** the actual read found CLI and server both at `0.31.1`.
  The claim that this pinned version is from 2024 was not substantiated; the image
  was not bumped merely because of that assertion.
- **Quote/claim caps and output budget:** 240 characters, six claims and 600 output
  tokens are candidate settings, not established optima. Lowering an output limit
  does not prevent a length cutoff; it can cause one sooner. Preserve the current
  contract until an experiment supports a change.
- **Context trimming:** fewer generation passages would change the effective
  generation context and must be evaluated/documented as such. Retrieval@5 alone
  would not validate a generator consuming only three. URLs/source versions were
  not silently removed from the prompt or exported provenance.
- **Reranking:** plain Python does not automatically make a new metadata heuristic
  course-demonstrated. An answer judge does not automatically establish a taught
  listwise document reranker. Keep specific-use source evidence as the boundary;
  RRF is taught under reranking and the double-credit interpretation remains open.
- **Cross-judging:** two judges may expose disagreement but agreement is not truth.
  Direct assistant review is the first route. Fixture calibration applies only if
  the automatic judge is used; no expert review is invented.
- **Evaluation rules:** a one-question slice-regression allowance is not justified
  by statistical insignificance on seven questions. A held-out split reduces some
  tuning bias but is not automatically an unbiased population estimate, especially
  with provisional agent labels and overlapping publications/topics.
- **Runtime timing:** do not edit runtime code while a measured experiment runs;
  this repository intentionally detects changed code. Independent documentation
  work can continue without changing the runtime fingerprint.
- **Images/demo traffic:** capture real runtime output, label previews and QA
  activity honestly, and never mark an agent demo as researcher feedback to make a
  chart look populated. A preview image is not evidence of live generation.
- **Packaging:** the existing explicit encoder initializer already addresses the
  hidden first-query download. Baking weights into every image is an alternative
  with rebuild/size costs, not a required replacement. Current Compose remains
  unexecuted and now initializes only the first required model.
- **Fresh clone:** a clone/worktree of the existing HEAD would omit uncommitted
  remediation. Reproduce the actual approved release commit after it is created;
  a working-tree export must be labeled as such. Do not call an old-HEAD run a test
  of these changes. Preserve volumes and unrelated services.
- **Presentation:** improve navigation and explanations, but do not remove pending
  rubric rows or material setup failures while they remain true. Added dependencies
  named in the notes are not all untaught; unnecessary tool coverage is the reason
  to avoid them here, rather than a blanket claim that the course never taught them.
- **Release/cloud:** user authorization for code improvement is not authorization
  for installation, publication or submission. Public exact-commit access and peer
  reviews remain release requirements. Cloud and discretionary points are unclaimed.

## Course and compatibility evidence

The [official project rubric](https://github.com/DataTalksClub/llm-zoomcamp/blob/main/project.md#evaluation-criteria)
was reread: maximum core credit depends on the implemented flow and evaluations,
not a mandated model count. Its direct-LLM/no-knowledge-base one-point tier must not
be confused with a knowledge-base-only preview. Full Compose configuration and
proven reproducibility are distinct judgments. Past project totals without grader
comments cannot reveal which technology caused an award. This update does not
supply new per-criterion peer-review reasons or rescore those projects.

[Ollama's compatibility documentation](https://docs.ollama.com/api/openai-compatibility)
supports the JSON object adapter. [Model metadata](https://docs.ollama.com/api-reference/show-model-details)
and [loaded-model metadata](https://docs.ollama.com/api/ps) support the new diagnostic.
Current [context documentation](https://docs.ollama.com/context-length) does not
justify assuming one fixed allocation for every local installation. Taught-route
attribution and adapter boundaries are in [course sources](../../docs/course-sources.md).

## Minimum remaining execution sequence

1. After owner approval, download **Phi3 only** into existing Ollama. Run
   `check-runtime` and the existing offline `prepare-encoder` check. Preserve the
   reported weights digest; do not substitute the installed Gemma 3 model.
2. Run the six-question/two-prompt pilot. Inspect every raw output and validation
   failure. If the contract is unusable, make one documented change and start a new
   run, retaining failures. Do not hand-edit model outputs.
3. Run the full one-model/two-prompt development comparison. Complete all explicit
   assistant reviews, summarize, preview selection, then apply the justified winner
   to the application. Verify its configuration and evidence fingerprints. If
   everything is unacceptable, no winner is promoted.
4. Freeze and run the held-out evaluation. Keep disappointing results. Perform a
   generated-answer browser walkthrough: sources, JSON/CSV, stored answer ID,
   feedback and monitoring. QA feedback remains QA.
5. After separately approved Docker setup, build/rehearse the full stack and
   PostgreSQL persistence/outage recovery. Reproduce the exact release tree from
   the documented setup, not the author's existing environment. Update readiness
   only from those artifacts.
6. Seek release approval for the concrete reviewed tree, then verify public access
   to the exact submitted commit and current cohort requirements. Submission and
   required peer reviews remain user-controlled.

The conservative prior estimate remains **14/26**, with RRF overlap unresolved.
The remaining core evidence is R02 +2, R04 +2 and R09 +1. More software tests do not
award those points. No passing grade, instructor approval or submission readiness
is promised. The latest [delivery check](delivery.json) records the actual work and
limits of this update.
