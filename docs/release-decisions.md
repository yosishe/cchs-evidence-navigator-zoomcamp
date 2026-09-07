# Public release: decisions, experiments and limitations

This is the first intended course submission of this owner's project. It is a new
working-tree snapshot, not a reuse of a previously passed submission. The original
private repository remains unchanged. See the [import manifest](../reports/release-migration/baseline-import.json)
and [protected contract](../reports/release-migration/protected-baseline.json).

## D25 — Explicit owner exception for Gemma 3 12B

**Decision:** compare the installed `gemma3:12b` with taught `phi3` through the
existing local Chat Completions route. The owner approved this exception on
2026-09-07. Gemma 3 is **not** labeled taught. Its installed Q4_K_M artifact is
restricted to digest `f4031aab637d1ffa37b42570452ae0e4fad0314754d17ded67322e4b95836f8a`.

**Rationale:** previous small-model pilots had actual omissions and invalid output;
a stronger generator is a testable hypothesis, not an established fix. Taught
Phi3 and Gemma 2B remain alternatives; another provider/framework is unnecessary.
**Trade-off:** approximately 8.15 GB of model files, higher working memory and
latency. Native macOS acceleration does not establish CPU-container feasibility.
**Verification:** paired model/prompt pilot, complete development comparison when
justified, source-based review, actual serving-context and usage receipts.
**Revisit:** insufficient quality, resource failure, changed weights or loss of
critical source support. Do not silently substitute another model or cloud API.

Course provenance: [2024 local-model example](https://github.com/DataTalksClub/llm-zoomcamp/blob/main/cohorts/2024/02-open-source/qa_faq.py).
The course [permits explained alternative technologies](https://github.com/DataTalksClub/llm-zoomcamp/blob/main/project.md#technologies);
the owner's original boundary was narrower. This model exception changes neither
the corpus nor the frozen answer-quality criteria.

## D26 — Numbered citation transport with exact canonical recovery

**Decision:** a request-local integer selects a supplied passage. The application
maps it to the unchanged source/window ID. Raw `text, passage, quote` becomes the
existing `text, evidence_id, exact_quote` contract before validation and export.
This is our adaptation of Module 1 context/prompt composition, not a new scientific
method. Earlier `short_ids` work is a predecessor, not independent proof of benefit.

**Alternatives:** retain full source IDs; retain E1-style aliases; fuzzy quote repair.
The first two remain experimental alternatives. Fuzzy matching is rejected: a
similar string can change a negation, count or identifier. Only whitespace can be
normalized, and the match must be unique within the specified passage. Case,
punctuation, identifiers and numbers remain exact. Ambiguous matches fail closed.

**Trade-off:** simpler copying may improve format reliability, at the cost of a
mapping layer and rejection of ambiguous quotes. The canonical answer, source
version and export remain application-owned. Raw quote and exact character-offset
receipts are retained and replayed by the selection verifier.
**Verification:** adversarial transport fixtures plus paired real generation.
**Revisit:** source-identity ambiguity, measurable answer regression or unnecessary
complexity. Mechanical quote recovery never proves the claim's meaning is supported.

## D27 — Partial coverage is diagnostic, never a replacement pass rule

**Decision:** report separate covered/partial/missing/uncertain counts for facts
and qualifications, per arm and slice. No arbitrary 0.6/0.2/0.2 composite is adopted.
Empty requirements have denominator zero and rate null, not perfect coverage.

**Rationale:** all-zero full-answer results can conceal partial progress. Counts
explain failure without relabeling an incomplete answer as complete.
**Trade-off:** richer reports require explicit agent annotation and remain
provisional. A true quote with a wrong conclusion, an omitted qualification or an
unsupported limitations sentence still fails. Whole-answer/export review is mandatory.
**Verification:** known partial/unsupported/abstention fixtures retain rejection;
every actual output is reviewed against frozen reference requirements and sources.
**Revisit:** demonstrable evaluator error requires preserved old/new versions and
a fair rerun of both candidates; never change labels to fit a model output.

## D28 — Fixed experiment conditions and conditional promotion

The [pilot plan](../reports/release-quality/pilot-plan.json) declares 12 development
questions (two per slice), two models and two prompts: 48 planned generation calls.
Two additional calls assess feasibility and are excluded from pilot quality totals.
No model judge is used. The review phase is an assistant source audit, not an
independent clinical or human study. Failed attempts remain in the denominator.

The retrieval factorial tests vector/hybrid and top-k 5/10 on all 42 development
questions, holding boosts, candidate pool, corpus and encoder fixed. The old
title-weight-zero hybrid experiment is different; its results cannot be substituted
for the new unchanged-boost arm. More context can improve coverage and also add
distraction, delay and truncation. Inspect individual losses before broadening.

Only justified alternatives proceed to a full paired 42-question generation
comparison with the same chosen retrieval contexts. Pilot success is not promotion.
The existing strict contract applies: no unsupported/critical regression, useful
complete supported research answers, actual app selection and reproducible flow.
If no candidate meets it, retain the failing evidence and continue a focused repair.
Do not apply a best-of-failing candidate. Final questions do not choose the candidate.

## D29 — Prepare publication without exposing the private worktree

Copy only reviewed project assets; preserve article attribution and per-source
licenses. The noncommercial article terms are not replaced by a repository code
license. Do not publish local secrets, weights, personal files or runtime databases.
Historical model outputs/metrics are retained and explicitly historical. Sixteen
historical reports have owner-local path metadata replaced by placeholders in the
public copy; [the redaction ledger](../reports/release-migration/public-path-redactions.json)
preserves before/after hashes and identifies them as derivatives. The originals
remain unchanged in the private predecessor.
Current evidence uses the new version and actual calls. No official points are
assigned without a course record for this exact submitted commit.

The full Compose route initializes the model named by the app config and verifies
its digest. Downloads are explicit setup operations, never inference fallback.
The host currently lacks Docker; clean build/start/restart evidence remains pending.
The public commit/push and course submission are separate owner-controlled steps.

## D30 — Repair retrieval context before attributing failures to model size

The [fresh factorial](../reports/release-quality/retrieval-factorial.json) held
title boost 2 and zero-based RRF constant 50 fixed. Hybrid/10 covered all annotated
references in 21/35 answerable development questions; vector/5 covered 18/35.
The subsequent [title ablation](../reports/release-quality/title-lexical-ablation.json)
and [fresh verification](../reports/release-quality/hybrid-zero-fresh.json) reached
26/35 with title boost 0, hybrid/10 and RRF 50. The ablation demonstrates a dataset-specific coverage effect. Shared publication
titles contributing scores to irrelevant chunks are a plausible explanation;
the result is not a general rule that titles should be ignored.

**Alternatives/trade-off:** vector/5 is cheaper and shorter; hybrid adds an encoder
and two rankings, and ten passages increase context and distraction. Smaller RRF
constants were also replayed against the same candidate pools. Rank replays are
not new retrieval calls. The apparent PAR-01 loss under frozen reference IDs was
inspected: retrieved Italian abstract passage 2 says retrospective analysis and
passage 21 says electronic medical record. Its facts are available in an unlisted
equivalent passage. The bank remains frozen; the earlier no-annotated-loss rule
and the reason for considering this higher-coverage candidate are both recorded.

**Verification/revisit:** identical fresh context artifacts feed both prompt arms.
Do not promote retrieval from reference counts alone; review complete answers,
every loss and actual serving context. Remaining misses include ranking failures
and known parser exclusions; parameter tuning cannot recover unparsed tables.

## D31 — Separate output shape from source precision

The [four-call format diagnostic](../reports/release-quality/format-diagnostic-disposition.json)
compared JSON object and schema modes on identical contexts. Both gave one complete
answer and one rejected comparison. Schema mode restored a missing field but kept
invented ellipses in quotes. It did not establish a quality gain and stays off in
the next paired prompt comparison. Four calls do not prove universal equivalence.

The [precision repair plan](../reports/release-quality/precision-repair-plan.json)
compares `numbered_evidence` with `numbered_precise`, keeping model, retrieval,
format and output budget fixed. The latter requires literal side-by-side figures
with original denominators, explicit objectives versus methods, specific data
types and contiguous quotations. It adds no reference answers or domain facts.
These instructions are our application of taught prompt/evaluation methods.

**Trade-off:** stronger specificity lengthens instructions and may increase
omissions/refusals. It cannot substitute for missing evidence or a semantic
review. Keep all errors and reject critical false statements; do not silently
repair arithmetic, relax quotes or label partial answers complete.

## D32 — CPU-specific container dependencies

**Decision:** preserve the tested native dependency lock and resolve separate,
hashed CPU-only Linux ARM64/AMD64 locks for the complete container image.
The original Linux resolution contained NVIDIA/CUDA packages despite CPU inference.
Use the same PyTorch release's official CPU build; other packages stay constrained
to existing `uv.lock` versions. No new application library is introduced.

**Trade-off:** smaller dependency surface and fewer unnecessary accelerator
packages, in exchange for two architecture-specific locks and no container GPU
route. Resolution is not a build or an inference benchmark. The actual clean
Compose rehearsal must still verify imports, vectors, source identities, model
execution, PostgreSQL and restart persistence. Revisit if pinned CPU artifacts
are unavailable or actual retrieval differs across the target environments.

Compatibility references: [official CPU installation guidance](https://pytorch.org/get-started/locally/#linux-installation),
[uv and PyTorch](https://docs.astral.sh/uv/guides/integration/pytorch/).

## D33 — Source-span transport after observed copy failures

**Observed problem:** both arms in the [24-call precision repair](../reports/release-quality/precision-repair-disposition.json)
delivered only 4/12 fully acceptable answers and had four malformed outputs each.
The precise prompt removed the observed critical semantic failure, but correct
intended answers still failed because the model rewrote quotations or omitted a
required field. Neither arm was selected. The old precise arm also omitted stored
resolution receipts due to an overly narrow prompt-name condition; those historical
records remain unchanged and cannot supply complete current selection evidence.

**Decision and scope:** extend the authorized numbered-passage adaptation with
lossless, locally numbered source spans. A model returns claim text and the integer
`passage`, `from_span`, `to_span`. The application copies that exact contiguous
range, owns all source metadata and records the original positions. A punctuation
heuristic only creates display boundaries; it is not an NLP sentence detector or
a new retrieval index. Every original character remains in the supplied window.
Source qualifications can be selected by the same pointers. The application
retains their literal text in the existing canonical limitations field and exports.

**Alternatives and trade-offs:** copying a short quote gives the model finer span
control but repeatedly introduced nonliteral ellipses. Fuzzy repair can silently
change scientific meaning and remains rejected. Position selection removes that
copying task and permits unambiguous repeated text, but introduces pointer errors,
potentially longer quotes and fragmented display boundaries. A real quote can
still be irrelevant to the generated claim. Semantic support, all required facts,
material qualifications and the whole-answer veto remain unchanged.

This is original application I/O glue based on course context composition and
source attribution, not a method claimed to be demonstrated by an instructor.
It adds no runtime library. Schema output mode is fixed on for the pointer-shaped
feasibility run; that bundled change is not a prompt-only causal comparison.

**Evidence and continuation:** [146 software checks](../reports/release-quality/source-spans-software-check.json)
cover invalid/noninteger/reversed pointers, unchanged negation/numbers, duplicate
text positions, source-owned metadata, source qualifications and canonical exports.
The [five-call feasibility plan](../reports/release-quality/source-spans-feasibility-plan.json)
predeclares objectives, record types, a cross-source comparison, a qualification
and an unsupported premise. Real quality remains to be reviewed. Expand only after
a useful complete supported comparison and no observed critical failure. Reopen
the design if pointer accuracy, context overhead or semantic fidelity fails; never
weaken the frozen answer requirements or reroll failed outputs.

## D34 — Evaluate source-excerpt answers after paraphrase citation failures

The first [source-span feasibility](../reports/release-quality/source-spans-feasibility-disposition.json)
returned five structurally valid outputs, but one comparison attached the Italian
design/count/period to a generic study-summary span. Only 3/5 answers were fully
acceptable. The [shorter-prompt diagnostic](../reports/release-quality/source-spans-concise-diagnostic-disposition.json)
delivered 2/5 complete answers, two invalid outputs and a partially supported
record/count claim. Neither route passed the required comparison gate.

**Decision:** test a different answer style: the model selects original source
excerpts with one global span ID. The application copies the excerpt into the
existing canonical claim text and quotation fields and labels its origin. The
model still reasons about which evidence answers the question; it does not write
an additional scientific paraphrase. It may select several source rows and source
qualifications for the same question. No source data, benchmark fact, acceptance
rule or dependency is changed. This is an original prompt/output adapter around
the taught local RAG and exact source-record lookup, not a newly attributed course
algorithm or a validated scientific method.

**Why this fits the task:** evidence navigation and literal tag preparation need
faithful, attributable material for a researcher. Source selection can provide
useful side-by-side evidence without adding a false interpretation. The trade-off
is less fluent synthesis, longer or fragmentary excerpts and continued risk of
irrelevant or incomplete selections. A true quote is not automatically the answer.
The relevance, required-fact, qualification and whole-answer judgments still
control acceptance. Mechanical source copying receives no invented quality bonus.

**Implementation:** `source_extract_concise` and `source_extract_complete` share
the same globally numbered source spans and raw schema. Each raw claim/limitation
contains only `span`; source identity, text and offsets belong to the application.
Canonical records/claim exports include `answer_style=verbatim_source_selection`.
The UI identifies the style; scientific and tag review stay pending. A foreign ID,
injected text/metadata, empty answered result or abstention with added evidence is
rejected, with its raw attempt retained.

**Validation:** [the current full software suite](../reports/checks.json) includes
source-position replay, export-style/qualification preservation and a true but
incomplete excerpt that still fails the existing evaluator. The
[ten-call feasibility plan](../reports/release-quality/source-extract-feasibility-plan.json)
compares both prompts on the same five cases and contexts. No success is assumed.
Expand only after a complete useful cross-publication comparison and no observed
critical misleading context. Revisit if selected excerpts are opaque, fail task
coverage or lose qualifications; preserve rejected alternatives and actual results.

## D35 — Preserve relevance failures even after exact quote recovery

**Observed evidence:** the completed six-slice source-excerpt pilot produced
6/12 fully acceptable answers with concise instructions and 8/12 with detailed
instructions. Both had zero malformed answers and one critical relevance failure:
a genuine ventilation excerpt was offered as a qualification of a different,
genetic association. These outputs are preserved and both arms remain rejected.
The detailed arm also supplied unnecessarily long, though attributable, excerpts.

**Decision:** test a separate `source_extract_checked` prompt using three explicitly
fictional selection examples. They illustrate correcting a study-design label,
selecting a qualification about the actual relationship, and refusing a missing
accession. The real question bank, reference facts and biomedical answers do not
enter these examples. This is our application of Module 1 prompt composition and
Module 4 controlled evaluation, not an instructor-endorsed biomedical method.

**Alternatives and trade-offs:** selecting literal spans removes copying and
paraphrase errors but can return irrelevant or incomplete text. A generated
summary is more fluent and compact, but the earlier measured candidates invented
or misattached support. Longer instructions/examples consume context and can
encourage over-refusal. Keep the same canonical validation, source-owned metadata,
whole-answer veto and completeness criteria. No model judge, fuzzy repair or
additional inference call is introduced. A truthful refusal of a retrieved-context
gap still fails an answerable benchmark question; it does not earn full credit.

**Retrieval evidence:** [six representation alternatives](../reports/release-quality/representation-results.json)
produced no across-the-board improvement. The title/content hybrid covers all
annotated references in 26/35 answerable questions. Content-only hybrid has a
slightly higher mean fractional coverage but only 25 fully covered questions and
loses some exact-identifier/comparison evidence. The current choice remains a
candidate pending answer quality. This follows the taught separation of document
encoding and retrieval evaluation; all observed losses are retained.

**Verification and revisit:** [five declared feasibility cases](../reports/release-quality/source-extract-checked-feasibility-plan.json)
include the available-design omission, missing-association context, a supported
comparison and an absent accession. Inspect every actual output against the
original sources. Escalate only a useful candidate with no critical misleading
selection to broader development review. Neither a nonzero rate nor a mechanically
correct citation is a release-quality certificate. If the prompt still fails,
record the failure and diagnose it rather than weakening the reviewer contract.

## D36 — A bounded selection explanation is diagnostic, not a judge

The [checked-prompt experiment](../reports/release-quality/source-extract-checked-feasibility-disposition.json)
recovered the available retrospective-design qualification but still selected
mutation background for the association caveat and answered the accession question
with a cohort description. Its 3/5 result, including one critical relevance error,
was rejected. No reference facts or original acceptance criteria changed.

**Decision:** test `source_extract_reasoned`. The same local generation request
first returns a brief `selection_note` (1–600 nonblank characters), then status and
source-span choices. The bound is a project output limit, not a course threshold.
The schema and prompt change together; this is not a clean prompt-only attribution.
The note remains inside `raw_output` as a model diagnostic and is never copied into
canonical claims, qualifications, comparison rows or tag proposals. Explanations
can themselves be wrong: neither their presence nor their confidence is review.

**Alternatives and trade-offs:** the existing pointer-only prompts are shorter but
showed repeated topic/relationship substitutions. A second model judge would add
latency, cost accounting and calibration and is excluded from this first route.
A short in-request justification may improve task matching with more output tokens;
it may also rationalize a wrong choice. The application does not parse its prose
to grant approval or infer source metadata. All original semantic/completeness and
whole-answer checks remain necessary, including inspection of diagnostic content
when reviewing exported raw evidence.

**Implementation/provenance:** this is original prompt and JSON I/O adaptation of
Module 1 RAG composition and Module 4 structured output/comparison. No new runtime
library, model family, paid provider, extra call or automatic retry is introduced.
The adapter removes only the declared diagnostic field before applying unchanged
source-pointer and canonical validation. Old prompt variants reject that extra
field, and malformed/unbounded notes fail explicitly.

**Verification/revisit:** eleven focused source-excerpt software tests pass,
including exclusion of the note from canonical claim exports and rejection of a
missing/invalid note. These tests do not establish model quality. The
[five-case feasibility plan](../reports/release-quality/source-extract-reasoned-feasibility-plan.json)
uses the same frozen contexts and known failure cases. Preserve raw attempts and
inspect all claims, qualifications, refusals and diagnostic assertions before
considering wider development work. No automatic default change follows.


## D37 — Submission candidate with an explicit quality exception

**Requirement and constraints.** The owner approved a three-paper submission
candidate with prominent disclosure of the failed internal quality bar, conditional
on a useful new native EXA-01 answer, correct ABS-01 abstention and all software,
source, export, persistence and package gates. The course form remains owner-only.
No new installation, model download, Docker resource change, evaluator/prompt/data
edit or final-18 inference is allowed. This dated submission-policy exception
supersedes earlier publication-only-after-quality-pass statements; it does not
change the quality contract or historical failed judgments.

**Options and decision.** Bind `gemma3:12b / source_extract_complete` with the
measured hybrid/top-10/title-0/RRF-50 retrieval and pinned weights. Keep rewriting
disabled and the 300-second timeout unchanged. The controlled twelve-question
pair, using identical retrieved contexts, produced 8/12 fully acceptable answers
versus concise 6/12. Both retained a critical LIM-01 relevance error. Eighteen
historical arms are an experiment inventory, not a uniform tournament. Later
five-case checked/reasoned/Phi3 variants did not resolve their critical failures.
[Full selection record and hashes](../reports/final/selection-2026-09-07.json).

**Trade-offs.** Original excerpt selection avoids model-owned metadata and
paraphrase/copy errors, while remaining verbose and vulnerable to irrelevant or
incomplete selection. The larger owner-approved, non-taught model consumes more
memory than Phi3. Its pilot-specific timing is not a native or container service
promise. Existing Phi3 container proof cannot be transferred to Gemma.

**Implementation and evidence.** Only `configs/app.json` changes operational
configuration. `selection_status` is `SELECTED_ON_DEVELOPMENT_RETRIEVAL_EVIDENCE`;
`generation_selection_status` is
`BEST_OF_EVALUATED_ALTERNATIVES_INTERNAL_BAR_NOT_MET`. The second value does not
start with SELECTED, so the existing final-quality gate stays closed. It permits
candidate use through the existing app without forging a selection artifact.
The answer's `config_id` hashes the full parsed configuration; a file-byte hash
and an effective-config hash are distinct and recorded separately. Unit fixtures
have explicit configurations; real shipped-config tests continue to read the app.
[Software checks](../reports/checks.json), [native demo](../reports/final/native-bound-flow.json).

**Verification and revisit.** Preserve every failed attempt and the source,
question, fact, judgment and runtime hashes. The new two-case demo is operational
proof only and cannot replace the twelve-case pilot or become an accuracy score.
Stop publication if usefulness, abstention, exports, storage or package checks
fail. To claim full internal quality readiness later, resolve relevance and
completeness through a separately approved development/evaluation plan. Do not
use a favorable five-case subset, mutate labels or enable final-set inference to
make a failed candidate appear selected. The rubric award remains the examiner's
choice; publication does not establish a saved course submission.
