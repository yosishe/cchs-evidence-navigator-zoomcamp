> **Public-release amendment (2026-09-07):** Work now targets the separate
> `cchs-evidence-navigator-zoomcamp` repository. The owner approved installed
> Gemma 3 12B as an explicitly non-taught model exception; all original quality
> gates remain. Earlier private-only/model-exclusion and execution-status statements
> are historical. Use [current release evidence](release-status.md),
> [release decisions](release-decisions.md) and [setup](setup.md) for this version.

# Goal-driven improvement and honest evaluation

This is the operating contract for the active project-improvement Goal. The
initial design was delivered separately; execution evidence is recorded under
`reports/goal-loop`. Writing the contract does not establish a passing project.
Use it with the [copy-ready Goal prompt](IMPLEMENTATION_PROMPT.en.md#goal-prompt)
and the existing [evaluation protocol](evaluation.md). Application methods remain
restricted by the owner's taught-course-only, local/no-payment policy.

## 1. Use Goal in this Codex conversation

The owner activated the improvement objective after completing the design Goal.
The committed design checkpoint is `4a64153`; the active improvement baseline and
protected evaluation contract are in `reports/goal-loop/baseline-freeze.json`.
Execution preserves the worktree and the stopped historical pilot. Current
experiments and their explicit rejection decisions are summarized in
[readiness](release-status.md#release-blockers-and-completion-rule).

In the composer, enter `/goal` and choose the Goal command, then supply the
objective. `/goal` inspects status; `/goal pause`, `/goal resume` and `/goal clear`
control it. A Goal keeps an objective across turns; a heading saying “Goal” inside
an ordinary document does not by itself prove that the feature is active. Check
the actual Goal status. This feature is already active here, so no settings change
is needed. See [OpenAI's verified usage instructions](https://learn.chatgpt.com/use-cases/follow-goals).

Use ordinary follow-up messages to steer the active work. Specify an experiment
or usage budget if desired; no budget has been invented for this user. Pause if
you need to inspect a checkpoint. Resuming work must inspect the actual process
and saved results before launching another model run. A log saying “running” is
not proof of a live process, and a polling timeout is not proof it stopped.

The [OpenAI iteration example](https://learn.chatgpt.com/use-cases/iterate-on-difficult-problems)
uses illustrative percentage targets. We do not import its 90% example as a
Zoomcamp threshold or add its optional evaluation providers/frameworks to this app.
Our stopping condition comes from the course requirements and this research task.

## 2. Define what a pass means before optimizing

Maintain three separate outcomes. Never add them into a single reward:

| Outcome | Authority and evidence | What it cannot establish |
|---|---|---|
| `SOFTWARE_CHECKS_PASS` | Executed contracts, ingestion, interface and persistence checks, with explicit scope | Answer quality, official points or scientific validity |
| `LOCAL_CORE_EVIDENCE_READY` | Every core rubric row has current evidence inspected against its wording; the quality and reproduction gates below also pass | An awarded 18/18 or guaranteed admission/certificate |
| `OFFICIAL_GRADE_VERIFIED` | Accessible course record for this exact submitted project/version, after authorized submission/reviews | Unrecorded criterion-by-criterion grader reasons |

The default next Goal targets **full defensible core evidence**, with useful,
source-supported answers. The course awards the actual grade. If the user instead
sets an official-score Goal, that Goal remains incomplete until the corresponding
course record exists and is verified; a local estimate cannot satisfy it.

The [official rubric](https://github.com/DataTalksClub/llm-zoomcamp/blob/main/project.md#evaluation-criteria)
has nine core items, each worth up to two points. Practices contribute up to three;
cloud and discretionary extras contribute up to five. Peer-review points are
separate. Preserve exact tiers by linking the official document; do not invent an
accuracy threshold, mandatory second model, automated judge or required human
biomedical study. The owner's course-only constraint is stricter than the course's
general technology permission.

Use this evidence map, with the existing [50-check checklist](pre-submission-audit.md):

| Row | Maximum | Reviewer must inspect this project's actual artifact |
|---|---:|---|
| R01 Problem | 2 | A clear research question, user, corpus boundary, useful output and failure example |
| R02 Retrieval flow | 2 | The same request traversing corpus retrieval, real local model, cited output and app |
| R03 Retrieval evaluation | 2 | Comparable retrieval runs, per-question ranks and active evidence-selected config |
| R04 LLM evaluation | 2 | Comparable real answers, explicit support/completeness reviews and selected runtime prompt |
| R05 Interface | 2 | Browser question, answer, citations, meaningful export and correctly linked feedback |
| R06 Ingestion | 2 | dlt output feeding the corpus actually searched; repeat-run source/ID reconciliation |
| R07 Monitoring | 2 | Saved feedback and at least five meaningful charts with traceable data and denominators |
| R08 Containerization | 2 | Compose covering the selected stack; artifact coverage distinguished from execution |
| R09 Reproducibility | 2 | A clean setup/restart rehearsal with pinned dependencies, accessible data and actual outputs |
| R10 Hybrid | 1 | Measured text/vector/fusion alternatives; using the weaker variant is unnecessary |
| R11 Reranking | 1 | Actual rank transformation and isolated evidence; disclose RRF credit overlap |
| R12 Rewriting | 1 | Original/rewrite pairs, preserved intent, harm cases and the actual implementation |
| R13 Cloud | 2 | Real accessible deployment; no point for a plan or GitHub repository |
| R14 Extras | 3 | Demonstrable useful additions with explicit reviewer discretion |

These artifacts include our stricter engineering acceptance expectations; they
are not verbatim additional course requirements. For example, full Compose
execution strengthens reproducibility even though R08 describes the Compose
artifact. Track proposed points and uncertainties row by row, separately from
observations; a JSON field containing `points: 2` is not evidence for two points.

## 3. Freeze the experiment contract

Start from an identifiable Git checkpoint. Record its commit, dirty-file list,
runtime-code/config IDs, corpus and source hashes, encoder revision, local model
digest, actual server/context settings, question-bank hash and evaluator version.
The first committed remediation checkpoint is `c74b743`; resolve its full ID with
`git rev-parse c74b743` when starting. Never reset away unrelated owner changes.

Freeze required facts, qualifications, answerability, splits, denominators and
critical failure definitions **before** viewing candidate outcomes. The active
bank has 42 development and 18 final-test questions; the old 13 are regression
cases. The three-question answer baseline is development evidence, not a holdout.
The final-test file is readable by the coding agent, so “not used for inference”
does not prove it was never exposed. Record actual exposure. Agent-authored labels
and shared publications/topics limit independence and generalization.

Do not show final questions, answers or grading labels in generation prompts,
special-case their IDs, or pass reference context to normal app inference. Known
reference context is allowed only in separately labeled diagnostics. Corpus text
and retrieved instructions remain untrusted data.

A label or evaluator defect can be corrected with an exact source-based reason,
old/new versions and owner-visible review. Re-evaluate both candidates under the
corrected contract; do not silently revise the rule after seeing a loss. Holdout
exposure requires an explicit record. Do not repeatedly create easier “new tests”
until the project passes.

## 4. The bounded iteration loop

1. **Verify state.** Inspect Goal status, active process handles, current code and
   previous checkpoint. Resume a confirmed live run; only start new work after
   confirming it is absent or terminal. Preserve receipts from interruptions.
2. **Pick one observed failure.** Locate the question, raw output, source and
   missing rubric evidence. Distinguish source/ingestion, retrieval, generation,
   validation, UI/storage, environment or evaluation failure.
3. **Predeclare one candidate.** Record the exact taught source, hypothesis,
   alternative, expected benefit, possible loss, affected slices and acceptance
   rule. Keep a baseline. Do not bundle prompt, model, retrieval and judge changes.
4. **Run a small development pilot.** Reuse the same retrieved context for prompt
   comparisons. Do not reroll an unfavorable completed answer. Count invalid
   outputs and attempts, including failures, against their correct denominators.
5. **Inspect, do not merely score.** Review every displayed sentence and its
   sources, then calculate counts using the rules below. Look at actual browser
   artifacts for UI work. Record how the proxy might still misrepresent usefulness.
6. **Keep, reject or revise.** A valid alternative must improve the intended
   behavior without breaking critical contracts. Mixed slice results require an
   explicit trade-off; preserve the incumbent while that trade-off is unresolved.
7. **Broaden only when justified.** Once the pilot is viable, complete the
   42-question paired development comparison and inspect each slice. Selection
   requires full current-version evidence. A nonzero best rate alone is not an
   adequate research-quality target.
8. **Validate the selected app.** Inspect selection before applying; verify the
   loaded config/model matches the experiment. Run affected contracts plus a real
   answer → source → export → save → feedback → monitoring flow. Rehearse clean
   Compose setup/restart separately, after required installation authorization.
9. **Freeze, then assess.** Use the final set once after selection. Do not tune on
   it. Retain any failures and the exposure ledger. If changes are needed, the
   exposed set becomes regression evidence; obtain a defensible new final
   assessment under an explicitly reviewed protocol, not an easier replacement.
10. **Audit completion.** Inspect every claimed rubric row and all quality gates
    against the candidate version. If a requirement remains weak, missing or
    blocked, report it and continue useful work. Never redefine success to match
    whichever subset currently passes.

Each iteration is bounded by its declared questions/configurations and a no-retry
policy, not an invented course call limit. The current one-model/two-prompt route
plans up to 12 pilot and 84 full development generation calls with rewriting off.
The one-selected-prompt final assessment uses 18 questions. Model/judge/rewrite
experiments add distinct attempts. Paid fallback is forbidden; local compute and
electricity are not free resources even when API billing is zero.

## 5. Evaluate usefulness and failure separately

Use [existing retrieval metrics](evaluation.md#retrieval-selection) and
[answer-review contracts](evaluation.md#answer-evaluation-and-judgment), augmented
by the mandatory whole-answer review below. These are applications of taught
evaluation, not an external grading service or a new RAG framework.

| Dimension | Procedure and denominator | Failure that a shortcut would hide |
|---|---|---|
| Retrieval availability | Classify every reference miss; distinguish excluded evidence from ranking error | Tuning rank parameters for a table never ingested |
| Retrieval quality | Hit/MRR plus required-reference coverage, all answerable development questions, broken down by slice | Counting one source as success for a two-source comparison |
| Mechanical validity | Parse every completed output; verify source IDs and exact nonempty quotation spans | An invented quotation with a plausible source URL |
| Semantic support | Judge each claim against its quoted context, including negation, population and study type | A true quotation attached to the opposite conclusion |
| Completeness | Judge every frozen required fact and qualification; missing/uncertain is not covered | Reporting 22 patients while omitting the requested period |
| Whole-answer support | Read claims, limitations, narrative and exported rows; give explicit supported/unsupported/uncertain verdicts and reasons | Correct abstention status accompanied by an invented premise |
| Abstention | For answerable questions, count unsupported abstention as end-to-end failure; for unanswerable ones require no unsupported substantive prose | Always abstaining to maximize citation precision |
| Reliability | Preserve malformed outputs, provider attempts, timeouts and interrupted runs | Removing errors from the denominator or retrying until lucky |
| Resources | Separate setup/search/generation/judgment/storage; use actual token counts and recorded attempts | Calling local inference costless, or hiding preparation time |
| User flow | Verify downloaded bytes, persisted answer/feedback identity and each chart's denominator | A screenshot of a button or fabricated “researcher” feedback |

The current CLI already enforces formal-claim support and required fact coverage
from explicit reviews. It **does not mechanically certify all free-form
`limitations` prose**. The implemented `navigator/whole_review.py` enforces explicit review coverage,
answer/export hashes and vetoes; it does not generate semantic judgments. Do not treat a passing
`review-answers`/`select-generation` result as sufficient on its own.

For each candidate save a `whole-answer-review.json` next to the results, containing
schema_version=1, the result hash, artifact-level `reviewer` and `reviewer_kind`,
and one row per answer ID/content hash plus the current export payload hash. Each
row records: `visible_prose_supported` (true/false/null),
`export_preserves_qualifications` (true/false/null), source-based reasons, observed
critical failures and an overall acceptable verdict. Null/unreviewed is not pass.
Every row must match the existing answer review; do not use a sidecar to upgrade
an answer the primary review rejected. Selection requires this exact sidecar filename beside `reviews.json`; runtime
verification binds its hash too. Copy `whole-answer-review-template.json`, review
every sentence and exported row, then save `whole-answer-review.json`. The
validator checks consistency; the underlying support judgments remain provisional
agent review, not automated semantic proof or independent human validation.

Use counts rather than a flattering percentage without its denominator. Report
answerable completeness separately from unanswerable abstention, and both by the
six existing slices. Report gains and losses for the same questions. Do not infer
statistical significance from the current small, provisional dataset. Temperature
zero does not guarantee identical repeats; if stability repeats are needed,
predeclare their count and retain all outcomes.

Agent review remains provisional. Blind candidate names and randomize review order
when practical, with a saved mapping. Evaluate the same source-based criteria on
both candidates; do not supply a desired grade to the reviewer. A separate review
phase by the same agent is not an independent human or external course assessment.
An automated judge remains optional and requires calibration if used.

## 6. Challenge the evaluator before trusting it

The purpose of a challenge is to make known bad behavior score badly. Keep
challenge fixtures clearly synthetic and out of the biomedical benchmark totals.
Existing [local-quality tests](../tests/test_local_quality.py),
[review regressions](../tests/test_review_regressions.py) and
[selection-integrity tests](../tests/test_instructor_reassessment.py) cover parts
of this matrix; do not claim all remaining semantic challenges are implemented.

| Deliberate counterexample | Required evaluator response | Current coverage / next check |
|---|---|---|
| Abstain on every answerable question, including in a mixed bank | Fail completeness/end-to-end usefulness; correct refusals alone cannot nominate a winner | Iteration 019 reproduces and repairs primary/whole/selector nomination, including loss of the only answerable success after a whole-answer veto |
| Give a true quote but omit one required fact | Reject full-answer acceptability | Executed completeness fixtures; DIR-02 real diagnostic |
| Drop a material qualification | Reject full-answer acceptability | Executed qualification fixture; inspect raw prose too |
| Invert negation or broaden a study result | Reject semantic support even if quote matches | Required source-based review; automatic string checks cannot prove entailment |
| Forge a source ID or quotation | Reject output, retaining the failed attempt | Existing identity/quotation fixtures |
| Place unsupported assertions only in limitations | Veto candidate despite valid status/claims | ABS-01 observed failure; mandatory whole-answer review, not automatic proof |
| Remove errors or duplicate a winning question | Reject comparison coverage/accounting | Existing pair/review/selection consistency checks |
| Change labels, judge or cutoff after seeing results | Invalidate the comparison until independently justified and re-run fairly | Git/contract audit and explicit version review |
| Feed answer keys or gold context into runtime | Reject as contaminated runtime evaluation | Inspect saved request messages; reference diagnosis stays separate |
| Optimize phrases to please an LLM judge | Reject unsupported response; score semantic evidence, not wording or verbosity | Manual challenge with altered answer phrasing and candidate-blinded review |
| Display five meaningless charts or seeded positive votes | Reject useful monitoring evidence; retain QA labels | Actual data/denominator review and origin-integrity tests |

If a counterexample passes, repair or supplement the evaluator before optimizing
the application against it. Keep that repair in a separate, reviewed change so
an agent cannot quietly lower the bar. Hashes establish file consistency; an
agent that can edit files can rehash fabricated evidence. Actual content review,
version history and owner/course review remain necessary.

Goodhart's Law motivates this separation: optimizing a useful proxy can eventually
harm the underlying purpose. [Manheim and Garrabrant](https://arxiv.org/abs/1803.04585)
describe multiple mechanisms. Our safeguards below are project applications,
not claims that the course teaches this paper:

- Avoid selection on noise: retain paired failures, all attempts and per-slice
  results; do not cherry-pick a lucky model output.
- Avoid extreme proxy optimization: one perfect citation out of one claim must
  not hide a mostly unanswered research question.
- Avoid replacing the real task with its metric: source/retrieval/answer/export
  must work through the actual user path, without benchmark-specific branches.
- Avoid manipulating the evaluator: freeze rules, review changes, audit raw
  evidence and retain an external distinction between estimates and awards.

## 7. Commands and evidence locations

Run commands from the repository root after approved setup. This design itself
performs no model download or generation. Commands below have different scopes:

```bash
# Software contracts; no evidence of real answer quality.
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 ENABLE_PAID_LLM=0 .venv/bin/python tools/run_checks.py

# Read-only metadata check; no generation. Specify a new output location.
.venv/bin/python -m navigator check-runtime --output runtime/goal-loop-preflight.json

# Inspect a no-call plan before generation; this rewrites reports/answer-plan.json.
.venv/bin/python -m navigator plan-answers --max-questions 6

# REAL local generation: only after inspecting the plan and available model.
.venv/bin/python -m navigator evaluate-answers --max-questions 6
# Later, when the pilot justifies full development coverage:
.venv/bin/python -m navigator evaluate-answers
```

Each answer run prints a new experiment directory. Preserve it. Copy its review
template to a new `reviews.json`, fill every judgment, and create the whole-answer
sidecar. The following path variables are placeholders to set to that actual run;
they are not files supplied by this design:

```bash
RESULTS_PATH=reports/experiments/answers-REPLACE_WITH_ACTUAL_RUN/results.json
REVIEWS_PATH=reports/experiments/answers-REPLACE_WITH_ACTUAL_RUN/reviews.json
.venv/bin/python -m navigator review-answers "$RESULTS_PATH" "$REVIEWS_PATH" \
  --whole-answer-reviews "$(dirname "$REVIEWS_PATH")/whole-answer-review.json"
.venv/bin/python -m navigator select-generation --results "$RESULTS_PATH" --reviews "$REVIEWS_PATH"
# Add --apply only after full evidence review AND the whole-answer veto checks.
```

Only after a valid frozen selection, run
`python -m navigator evaluate-answers --split test` with the same environment.
Use the [README](setup.md#full-compose-route--execution-pending)
for Compose instructions; a passing native run does not substitute for that
rehearsal. Rewrite experiments are separate and stay disabled by default.

Save a durable iteration journal under `reports/goal-loop/iterations/`, one file
per completed or interrupted attempt. Required fields:

```json
{
  "iteration_id": "ILLUSTRATION-NOT-AN-EXECUTED-RUN",
  "status": "PLANNED",
  "baseline_commit": "FULL_COMMIT_REQUIRED",
  "candidate_code_id": null,
  "config_id": null,
  "corpus_id": null,
  "question_bank_hash": null,
  "evaluator_version": null,
  "model_digest": null,
  "hypothesis": "Explicit coverage instructions may repair omitted requested facts",
  "taught_source": "docs/course-sources.md",
  "changed_dimension": "prompt",
  "split": "tuning",
  "question_ids": [],
  "planned_calls": null,
  "attempted_calls": 0,
  "raw_results_path": null,
  "review_path": null,
  "whole_answer_review_path": null,
  "metrics_by_slice": [],
  "new_failures": [],
  "decision": "NOT_EVALUATED",
  "rejected_alternatives": [],
  "tradeoffs": [],
  "rubric_rows": ["R04"],
  "official_points": null,
  "heldout_exposure": "NOT_USED_BY_THIS_ILLUSTRATION",
  "next_action": "Verify current runtime and freeze the experiment contract"
}
```

Also maintain a row-by-row rubric ledger with `observed_evidence`, `not_proven`,
`provisional_points`, `reviewer`, `reviewed_version` and `official_points: null`.
Do not turn the illustrative record above into executed results. Include actual
artifact hashes and commands/exit states in real records; relative paths must
resolve inside the delivered repository.

## 8. Completion and authorization boundaries

Before marking the next local-core Goal complete, prove all of the following:

- Every core row has evidence tied to the candidate; distinctions between
  observed behavior, static configuration and reviewer judgment remain visible.
- Retrieval and answer alternatives were fairly evaluated; the chosen app
  settings match their evidence. Full development coverage and the final
  assessment are present, with actual exposure history and whole-answer review.
- The five existing answer-quality dimensions plus the whole-answer veto are
  satisfied for accepted outputs. No known unresolved fabrication, ownership,
  qualification-loss or evidence-accounting defect is hidden by an average.
- The application produces a complete, supported answer for its documented
  research use cases and handles the frozen critical failure cases correctly.
  Broader corpus gaps and remaining noncritical errors remain reported. There is
  no claim that this small benchmark proves universal biomedical reliability.
- Real UI/export/storage/feedback/dashboard and clean Compose restart checks
  passed for the candidate; all relevant existing tests still pass without
  removal, weakened assertions or invented results.
- README, decisions and rubric ledger match the actual candidate. A restorable
  version exists. No official grade, publication, eligibility or certificate is
  claimed from this local condition.

If these conjunctions cannot be met, the Goal is incomplete. Continue independent
work while possible. Report a specific genuine blocker when authorization or
external state is necessary; never mark success because local model quality is
merely the best of poor alternatives. Never run a busy loop polling a stopped job.

The owner authorized a local commit of the work in this delivery. That does not
authorize future automatic commits, pushes, installation, cloud spending,
publication or submission. Preserve earlier authorization when explicitly given;
otherwise request the required action only after preparing concrete reviewable
work. Technical readiness is separate from the public exact-commit access and
peer reviews needed for actual course grading.
