> **Scope for this submission:** the evaluator and quality contract below are unchanged. The bound candidate failed the internal bar and is used only under the disclosed [D37 submission exception](release-decisions.md#d37--submission-candidate-with-an-explicit-quality-exception). Earlier incumbent/promotion statements describe historical experiments. No final-split inference is claimed.

> **Public-release amendment (2026-09-07):** Work now targets the separate
> `cchs-evidence-navigator-zoomcamp` repository. The owner approved installed
> Gemma 3 12B as an explicitly non-taught model exception; all original quality
> gates remain. Earlier private-only/model-exclusion and execution-status statements
> are historical. Use [current release evidence](release-status.md),
> [release decisions](release-decisions.md) and [setup](setup.md) for this version.

# Evaluation protocol

For repeated improvement, use the [Goal loop and anti-gaming contract](goal-loop.md),
including its mandatory whole-answer review of free-form prose. Selection now requires a complete `whole-answer-review.json` sidecar and binds
its answer/export hashes. CLI validation checks review consistency, not the truth
of an agent's semantic judgments.

The current evidence and limits are in [remediation v2](review-remediation-v2.md).
The earlier 13-question bank and reports remain historical regression evidence;
the current corpus must use `data/evaluation/questions-v2.json`. To rerun the 13
exposed questions, use `python tools/evaluate_legacy_regression.py`. It remaps
exact source quotes to current windows and reports 39 searches separately; it
cannot supply answer-completeness labels or independent test evidence.

## Evidence unit and splits

The [completed single-prompt diagnostic baseline](../reports/answer-baseline/README.md)
contains three real development outputs, explicit assistant reviews and raw
receipts. Both answerable questions were incomplete; the absent-evidence question
had a correct abstention status with a wording concern. These selected cases are
not a representative quality estimate. Their examiner-record format is not the
CLI selection format; copying them into the repository does not complete the
separate 9-of-12-call paired pilot or nominate a generation winner.

A question has a stable ID, slice, split, answerability, exact source quotations,
required facts and required qualifications. All windows containing the same
reference quotation are acceptable IDs; overlapping windows are not independent
scientific findings. Reference coverage counts the required reference entries
present in top-k, while Hit/MRR counts any relevant-ID hit. Multi-source questions
can therefore have a hit while still lacking enough evidence for a complete answer.

The 60-question design is a project assumption, not a course rule. Seven questions
per slice are for tuning and three for final testing. No source reference passage
crosses splits; publications and topics still overlap. Agent labels are provisional.
The final test is not run while model/prompt/rewrite selection remains open.

The capped six-question pilot now covers all six slices. Explicit `--question-ids`
must belong to the requested split and cannot be combined with a cap. The matrix
shares immutable contexts across both models/prompts. Review summaries preserve
per-question support/completeness/abstention reasons and per-slice numerators and
denominators. Automatic judging requires a passing five-fixture calibration bound
to the same installed judge digest, instructions, temperature and output budget;
fixture/review hashes are verified. This narrow check is not biomedical validation.

`select-generation` validates complete current-code development results, source
and question-bank hashes, and explicit agent reviews. It compares at least two
alternatives, then breaks quality ties by unsupported claims, errors, generation
latency and stable names. Candidates must have at least one acceptable answerable
response after whole-answer review and no critical or unsupported-claim failure.
Correct refusals remain counted but cannot establish a useful generator alone.
These are necessary eligibility conditions, not research readiness. Preview is
separate from `--apply`. Runtime checks reject
a selected configuration whose code, parameters, corpus or evidence differs.

The final-test command uses one selected model/prompt and all 18 questions. It
cannot nominate a winner. Corrected-version reruns after test exposure are
regression evidence. Blocked/incomplete CLI runs exit nonzero; executed generation
can still await review. Frozen preparation timing and actual generation timing
are reported separately, so preparation must not be counted twice.

## Retrieval selection

`tools/evaluate_retrieval_v2.py` compares 1000/150, 750/150 and 500/100 character
windows with title+content versus content-only vectors, and lexical/vector/hybrid
retrieval. Candidate depth is 20; output depth is 5; manual RRF k=50 uses zero-based
ranks. These are explicit project experiments, not universal optimal values.

Reject silent encoder truncation. Select highest development reference coverage,
then Hit, then MRR; break remaining ties by fewer windows and simpler retrieval.
Current result: vector, 750/150, title+content, 377 windows, no truncation. The full
rank traces permit a fixed-candidate RRF audit. The selected method is not chosen
to maximize a technology checklist.

For each miss, distinguish source absent, evidence excluded, missing label,
candidate absent and poor final rank. Missing an incomplete reference label does
not establish that every alternative is irrelevant. Report errors by question
slice and retain failed cases. Tables/figures remain an explicit coverage gap.

## Answer evaluation and judgment

Use `evaluate-answers` first: one taught model, two prompts and explicit assistant
review. The two-model matrix is optional. Fix question/context across alternatives.
Each result binds config/corpus/question-bank hashes; every API attempt
has a receipt, including failure. Interrupted runs cannot be treated as completed.

The revised evaluator distinguishes unavailable infrastructure from a completed
invalid answer. Provider/preflight errors stop the run. A completed response that
fails JSON or citation validation, or reaches the output-token limit, remains an error with no displayed claims, but
the other prompt still runs. Every planned pair must be reviewed; errors stay in
the denominator and count as unacceptable. `REVIEWED_COMPLETE` describes coverage,
not a perfect-quality result. Selection independently parses each failed raw output
to confirm it actually fails validation; changing a valid output's status to
`error` cannot manufacture a losing alternative. There are no automatic retries.

For an invalid answer's review: relevance=`not_relevant`, claim_support=`[]`,
required fact/qualification labels=`missing`, abstention_correct=`false`, and a
reason identifying the recorded validation failure. For a valid answer, inspect
each claim and each required reference fact separately; an exact quote does not
by itself establish support or completeness. Empty reference arrays for an
unanswerable question follow its frozen specification, not an exemption from review.

Judge five dimensions separately:

1. Schema and output ownership: application IDs/metadata cannot be overwritten.
2. Citation integrity: source exists and quotation is an exact nonempty substring.
3. Entailment: each claim is supported in the cited context.
4. Completeness: all required facts and qualifications are covered.
5. Abstention: absent evidence is handled without inventing an answer or claiming
   that a finding is absent from all literature.

An acceptable answerable response must be answered, relevant, contain supported
claims and cover every required fact/qualification. A correct fragment is not a
complete answer. An unanswerable response must abstain with no claims. Uncertain
judgments do not pass. Correct abstention on inadequate retrieval may be safe but
is still an end-to-end failure for an answerable question.

If using an automatic judge, calibrate it on the five explicitly fictional
fixtures before accepting its scores. This does not block the explicit assistant
review route. The fixed Phi3 judge makes comparisons consistent but shares a model with
one candidate, which introduces a potential bias. Inspect its raw inputs/output
and use a separate agent review; neither is biomedical expert validation.

Record candidate model/prompt, acceptable response numerator/denominator,
unsupported/partial claims, missing facts/qualifiers, abstention, errors, input and
output tokens and latency. Candidate selection uses development quality first,
then errors, latency and simplicity. Zero-quality, incomplete and test-only runs
cannot nominate a winner. No automatic configuration promotion occurs.

## Diagnostics and rewriting

`diagnose-answers` replays failed answerable cases with reference evidence. If the
answer improves, retrieval is implicated; if not, inspect prompt/model/reference
requirements. This is a diagnostic comparison, not a replacement benchmark score.

`evaluate-rewrite` uses one local request per question, preserves exact identifiers
and negation cues and falls back to the original query on error. These guards do
not prove semantic equivalence. Review dropped qualifications, changed scope and
new assumptions, and retain original/rewrite results and harm cases. Keep the
runtime switch off unless evidence justifies changing it.

## Reproducibility and metrics

Raw model/judge text and request messages are saved in call receipts; no private
patient data belongs in this corpus. Model downloads and real runs require setup
approval. Local API billing is zero; compute/energy is unmeasured. Missing token
counts are unknown, not zero. Retrieval setup, search and generation stages are
separate; database commit duration is not included in the generation chart.

After selection, record the exact runtime configuration/model digest, use the same
corpus and run the final test once. Preserve failures, proposed fixes and final-set
exposure. A completed run is not automatically proof of adequate research quality.

## Heading ablation — completed, not promoted

`HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python tools/evaluate_heading_ablation.py`
compares six predeclared variants on all 42 development questions, with the same
377 windows, labels and final top-5. It uses the existing cached encoder and no
model-generation calls. It preserves the application configuration and keeps its
embedding receipts in a separate report runtime.

Baseline vector retains the highest mean reference coverage (0.5667). Heading
vectors score 0.5619 and reduce MRR from 0.4695 to 0.4171, with gains in some
comparison/limitation cases and losses in PAR-06/EXA-04. All vector variants have
zero encoder truncation. The interaction variant (heading text and vector plus
RRF) is not an isolated reranker experiment. Timings are one local run with cache
and process-order effects; they do not establish latency significance.

See [full results](../reports/decision-refinement/heading-ablation.json) and
[the completed decision](decisions.md#d12). Do not promote a slice-specific gain
without accounting for regressions elsewhere. No final-test retrieval or generation
was run in this experiment.

## Instructor reassessment: selection evidence consistency

Before selection, complete question records must equal the active development bank,
not merely share its IDs and a claimed bank hash. Reconstruct each context from the
recorded question, filters, rewrite and source fields; check its corpus membership.
Bind model/prompt/settings, request messages, actual raw output and reviewed answer.
A nonempty context needs one completed generation receipt. SDK-injected fixtures
are labeled `sdk_fixture` and cannot nominate a live winner. No server authenticity
is inferred from hashes alone.

Selected calibration paths are repository-relative and fixture/review hashes remain
checked after selection, without another judge call. The new adversarial tests
rehash deliberately inconsistent artifacts and require rejection. See the
[instructor reassessment](../reports/instructor-reassessment/report.en.md).

## Reference-miss diagnosis from the selected retrieval policy

[Raw cases](../reports/claude-remediation/retrieval-misses.json) and
[review CSV](../reports/claude-remediation/retrieval-misses.csv) come from 35 new,
offline, cached-encoder searches on answerable development questions. The active
configuration, corpus, labels and held-out split were preserved.

| Reference-entry location | Count | Appropriate next experiment |
|---|---:|---|
| Top 5 | 36 | Check semantic sufficiency and completeness in generated answers |
| Ranks 6–20 | 16 | A permitted candidate-ranking experiment may help; isolate its contribution |
| Outside top 20 | 15 | Diagnose representation/query/source restriction before reranking |

These are 67 reference entries, not 67 independent passages or studies. Fourteen
questions have no top-5 reference hit; 17 lack complete reference coverage. The
labels are provisional and may miss valid alternative evidence. This diagnosis
cannot establish whether all needed literature or excluded table evidence exists.
Reranking cannot recover an item outside its supplied candidate set. No new ranker
was installed and no metric-based configuration promotion occurred.

## Change promotion with regression controls

This is our project-specific application of [Module 4 paired evaluation and the
existing course boundaries](course-sources.md), not a course promise that scores
cannot fall. A grader can revise an earlier estimate; a finite test set cannot
guarantee behavior on every future question. Preserve the working baseline and
promote a candidate only after a documented comparison. These gates supplement
the CLI's selection checks; they are not yet an additional automated gate.

| Priority | Isolated work | Required evidence before keeping the change | Trade-off and rejection condition |
|---|---|---|---|
| 1 — make existing work reviewable | Package actual single-prompt outputs/reviews and correct stale readiness statements; completed in `reports/answer-baseline` | Original and packaged file hashes match; runtime/config/corpus/labels unchanged; failures visible | Improves reviewability, not answer quality. Never count copied calls as new replications or a complete comparison |
| 2 — fix generation omissions | Compare an explicit minimal output example plus coverage instructions with the current prompt, on identical retrieved contexts | Review schema, quotes, semantic support, every required fact/qualification and all visible prose; preserve per-question wins and losses | More instructions/output may cost tokens and time. Reject gains that introduce unsupported claims, lose required qualifications or weaken source validation |
| 3 — diagnose each retrieval miss | Separate missing/excluded source, incomplete label, missing candidate and low rank; vary one taught retrieval setting at a time | Per-question candidate/rank traces and reference coverage for all development slices | Deeper contexts can add distraction and latency. Keep the current vector default while hybrid/heading variants are weaker by the declared selection rule |
| 4 — prove clean reproduction | Rehearse the pinned Compose stack after required environment setup; ingest, answer, save, feedback, charts, restart, retained records | Exact version, commands, actual logs and UI/download checks; no undeclared host-only cache/service dependency | CPU container inference may be slower than native macOS. Record that difference; a changed container path must not silently replace the measured native configuration |
| 5 — optional rewriting | Compare original and one bounded local rewrite, keeping source identifiers and question intent | Paired retrieval/answer results, intent review, harm cases, fallback tests and incremental latency | An extra call can distort scope or worsen exact-identifier retrieval. Leave disabled if benefit is not established |

For priority 2, DIR-02 already retrieves the cohort count and period but omits the
period in its answer. DIR-01 fails even with known reference context when quotation
fields are missing. ABS-01 shows why unsupported premises must be reviewed in
limitations text as well as formal claims. A minimal complete JSON example and
instructions to cover each requested component are a prompt adaptation to test,
not a measured fix or a biomedical method taught by the course. See [D08](decisions.md#d08).

Do not change model, quote-length limit, source-ID representation and prompt
simultaneously. Short context aliases may reduce copying errors, but require
lossless application-owned mapping back to the original source IDs and adversarial
identity tests before use. Arbitrary caps on claims/quotes can remove necessary
qualifications; no new cap has been adopted. The pilot's recorded `length` finish
is an output-budget exhaustion, not evidence of a request timeout. Any change to
how that outcome is counted must preserve the failed output and denominator.

Use this promotion procedure for each candidate:

1. Preserve the incumbent config/code identity, corpus, question bank and raw
   evidence. Candidate output goes to a new experiment location. Record its exact
   course source, adaptation, rejected alternatives and expected failure it addresses.
2. Run a small development pilot first; freeze the retrieval context when testing
   generation. If output remains structurally invalid or incomplete, retain the
   diagnostic failure and revise the candidate before spending on a larger local run.
3. Evaluate complete development coverage under the existing protocol, reviewing
   all pairs and retaining invalid outputs. Report by slice and question, with
   numerators/denominators; an aggregate gain must not conceal a newly unsupported
   answer or an exact-identifier/qualification regression.
4. Keep source ownership, exact quotations, abstention behavior, export provenance,
   answer-linked feedback and provider boundaries as acceptance requirements. A
   candidate that breaks one stays unpromoted. If results trade quality between
   slices, explain the trade-off and retain the incumbent while it is unresolved.
5. Record token use and measured latency separately from retrieval setup and
   storage time. There is no invented universal response-time cutoff. Prefer the
   simpler/faster candidate when quality and critical behavior are equivalent.
6. Inspect selection before applying it. Verify the app loads the evaluated config
   and model digest; repeat the affected contracts and a real UI-to-storage flow.
   Keep a restorable configuration and its matching evidence; do not delete the
   previous run. An unacceptable best-of-bad-options result is not research readiness.
7. Freeze the chosen version, then use the full held-out set once as final
   assessment. If it reveals a failure, report it and fix it; the exposed set then
   becomes regression evidence rather than a fresh independent test. Complete
   clean reproduction before preparing a reviewer-accessible release.

The most direct remaining core-credit work is the second final-answer evaluation
tier and complete reproduction. More frameworks, a second model or an automatic
judge are not substitutes for those observations. Cloud and discretionary extras
remain separate; do not compromise a working local path to chase uncertain points.

## Explicit prompt candidates and whole-answer review

The active experiment ledger is in [readiness](release-status.md#release-blockers-and-completion-rule).
The implemented candidates `coverage_first`, `schema_first`, `course_user`,
`plain_context`, `short_ids` and `compact_metadata` are experimental options; none is a promoted
configuration. `short_ids` maps request-local labels back to immutable passage IDs
before validation. Review raw labels, the application-owned mapping, the canonical
answer and actual export payload together. Do not accept an invalid quotation or
unsupported conclusion because the citation label was copied correctly.

Iteration 010 disables JSON object mode only; every other setting and the frozen
contexts match iteration 006. Its decoded outputs are unchanged in all six cases.
This finding rules out that setting as the explanation for those six failures;
it is not a claim that format mode never matters. Known-reference diagnostics use
a separate diagnostic split and cannot supply selection evidence. All underlying
required facts, qualifications, question splits and acceptance rules stay frozen.

The incumbent remains `evidence_first`. The `coverage_first` candidate is an
original application of Module 1 prompt composition and Module 4 paired
evaluation; its complete-answer instructions are not a taught biomedical method.
Use `--prompts evidence_first coverage_first` on `plan-answers` and
`evaluate-answers` for a development comparison. Final-test overrides are rejected.
The seven-question pilot adds the already exposed DIR-02 omission case to the
six-slice pilot: 14 planned generation calls, with identical context within each
pair and unchanged model, retrieval, temperature and output budget.

For every run fill both `review-template.json` and
`whole-answer-review-template.json` as new `reviews.json` and
`whole-answer-review.json`. Review all visible prose, exact cited text, required
facts/qualifications and exported rows. Run `review-answers RESULTS REVIEWS
--whole-answer-reviews WHOLE_REVIEWS`. Unknown judgments fail acceptance; the
sidecar cannot upgrade a primary rejection. `select-generation` requires the
sidecar, rejects critical failures and still requires all 42 development questions.

A length-limited output retains a completed provider receipt with actual usage;
the answer is rejected even if the returned JSON happens to parse. The evaluator
continues remaining planned pairs without retry. Real connection/timeout errors
still stop the experiment. Historical receipts are not rewritten.

Iteration 019 preserves the old evaluator and its two reproduced mixed-bank
failures in [the comparison record](../reports/goal-loop/evaluator-019-comparison.json).
The corrected primary nomination, whole-answer nomination and actual selector
exclude candidates with zero complete, supported answerable responses. This
enforces the already frozen all-abstention rule; it changes no reference fact,
qualification, denominator or prior answer judgment. The positive synthetic case
still selects a supported answerable candidate. All 14 saved result packets were
recomputed under both evaluator versions with unchanged per-question judgments
and counts. This is a software consistency check, not new semantic review or
current-code model evidence. The old partial pilot's obsolete whole-review format
remains explicitly invalid for selection.

## Retrieval rank replay and fresh cutoff checks

The [023 constant experiment](../reports/goal-loop/rrf-rank-replay-023.md)
reconstructs all stored k=50 fusion ranks/scores and compares the taught constant
grid with frozen labels. None of its cutoff-five candidates satisfies the
predeclared no-coverage-loss rule. The [024–025 cutoff experiment](../reports/goal-loop/retrieval-cutoff-capacity-024.md)
then finds two cutoff-ten candidates and verifies them through 84 actual offline
queries. Hybrid / 10 raises full reference coverage from 18/35 to 25/35 versus
active vector / 5 without per-question coverage loss against that baseline.

This is not a selected generation configuration. Compare the alternatives against
each other too: vector / 10 retains partial LIM-07 evidence lost by hybrid / 10.
Per-reference misses distinguish below-cutoff passages from entries absent from
the candidate lists. Preserve all six slices and the established denominators.
420 saved-rank replays are distinct from 84 fresh queries and zero new model calls.
Do not infer model context fit from character counts or encoder nontruncation.
Downstream answer/whole-export review and serving-token evidence remain necessary.

The [subsequent cutoff-ten answer pilot](../reports/goal-loop/cutoff-answer-026/report.md)
has now completed all eight calls and mandatory primary/whole-answer reviews.
Both candidates yield zero acceptable answers and four output errors. The better
retrieval proxy did not establish a useful generator. Keep vector / 5 active.
The observed 4,096-token allocation and nontruncated server releases concern
these actual completions, not arbitrary output budgets or all questions.

## Schema enforcement is not an answer-quality pass (027–028)

The optional `generation_json_schema` flag changes only the local generation
response format, leaving the exact citation validator and whole-answer review
mandatory. It is distinct from the `schema_first` prompt: either prompt can be
used with generic JSON mode or with a fixed schema. It is false by default and
cannot be combined with `json_mode=false` or used for a paid provider. Rewriting
never receives the generation answer schema. The transmitted schema is retained
in each new provider receipt, including failed attempts.

The [six-call format control](../reports/goal-loop/schema-answer-027/report.md)
has identical raw outputs to baseline. The [eight-call missing-field follow-up](../reports/goal-loop/schema-cutoff-028/report.md)
improves field presence but exposes unsupported or incomplete refusals. Both are
rejected. Empty exports and a correct refusal status cannot override false prose,
missing required facts or source-identity errors. Do not nominate either pilot
for full development or raise a rubric score merely because fewer outputs fail
parsing. New schema constraints, a model change or different context organization
must be predeclared separately and tested on the same frozen quality contract.
