> **Submission-candidate amendment (7 September 2026):** [D37](release-decisions.md#d37--submission-candidate-with-an-explicit-quality-exception)
> binds the measured Gemma/source-extract-complete/hybrid-top-10 candidate with
> its failed internal quality bar disclosed. The owner accepted this publication
> exception; original quality judgments and gates remain unchanged. The final
> 18-question inference test was not run. Earlier defaults, pending installation
> statements and private-only publication rules below are historical where they
> conflict with D37. Use [release evidence](release-status.md) and [setup](setup.md)
> for the current operating route.

# Implementation decisions and trade-offs

This is the current decision register. The dated log at the end is preserved for
provenance; it does not override the current cards. Each card follows the English
course handbook's D01–D17 build stages. [Course sources](course-sources.md) distinguish
taught implementations from our engineering adaptations. [Evaluation](evaluation.md)
defines the executable selection protocol. [Review response](../reports/decision-refinement/review-response.en.md)
reconciles the attached grading report with current evidence.

**Decision sequence:** requirement → constraint → demonstrated course options →
reasoned baseline → implementation → measured comparison → documentation → rubric check.
A leaderboard score cannot establish why a reviewer awarded a particular point.
A recommendation in an attached report is not permission to change project constraints.

## Constraints and decision rules

| ID | Constraint / known fact | Practical consequence |
|---|---|---|
| C01 | Owner requires taught methods, including labeled historical material | Cite the demonstrated use before adding an algorithm. The official rubric permits a broader toolbox; this restriction belongs to this project. |
| C02 | Zero paid providers/infrastructure; setup approval pending | Local course models only. Installed Gemma 3 is not automatically an allowed alternative. Never fall back to a commercial endpoint. |
| C03 | Agent review only; no biomedical expert labels | Label quality judgments provisional. Preserve uncertainty, population context and source type; proposals do not update a scientific registry. |
| C04 | Three clinical seed publications; tables not interpreted | Support literature navigation within this scope. Do not claim primary molecular PHOX2B coverage or an exhaustive review. |
| C05 | Hardware performance and live-model quality unmeasured | Pilot before committing to a large run. Character counts are not token limits; no invented CPU, memory, timeout or quality guarantees. |
| C06 | Development/test separation | Tune on 42 development questions; 18 final questions are reserved for selected generation. Exposed legacy questions remain regression evidence. |
| C07 | Private development; release under owner control | No publication, commit/push, submission or eligibility assumption as a side effect of improvement work. |

Choose quality and evidence integrity before optional scoring additions. Expected
latency/memory/quality effects below are hypotheses unless explicitly labeled
**Observed**. Exact defaults come from the active configuration or a declared
experiment, not a lecturer's universal recommendation. A new runtime-code hash
invalidates generation-selection evidence until it is rerun; documentation edits
alone do not. No generation configuration has yet been selected from live results.

## Navigation

| Stage | Decision | Course route | Main rubric relationship |
|---|---|---|---|
| [D01](#d01) | Useful research task | Module 1; optional example | R01 |
| [D02](#d02) | Corpus and evidence authority | Modules 1/7 | R01, R09 |
| [D03](#d03) | Ingestion and repeatability | dlt workshop | R06 |
| [D04](#d04) | Evidence units and headings | Modules 1/2; homework; chunking | R03, R09 |
| [D05](#d05) | Retrieval and filters | Modules 1/2/6 | R02, R03, R10/11 |
| [D06](#d06) | Encoder and execution environment | Module 2 | R03, R09 |
| [D07](#d07) | Complete shared flow | Module 1 | R02 |
| [D08](#d08) | Model, prompt and context | Modules 1/4; 2024 local models | R04 |
| [D09](#d09) | Rewrite, tools or agent | Module 1 function calling | R12 |
| [D10](#d10) | Reference labels and retrieval metrics | Module 4 | R03 |
| [D11](#d11) | Answer review and selection | Module 4 | R04 |
| [D12](#d12) | Controlled improvements | Modules 4/6 | R03/04/10/11 |
| [D13](#d13) | Inspectable research interface | Modules 5/7 | R05 |
| [D14](#d14) | Feedback and monitoring | Module 5 | R07 |
| [D15](#d15) | Packaging and reproduction | Module 5; 2024 Compose | R08/09 |
| [D16](#d16) | Reviewer evidence | Project guidance; Module 7 | All criteria |
| [D17](#d17) | Release and peer review | Official project instructions | Eligibility and submission |

<a id="d01"></a>
## D01 — Define a useful, bounded research task

**Purpose and entry facts.** Help a researcher locate, compare and export the
passages behind a CCHS literature question. Determine which named publications
and factual comparison are required before searching. Constraints C03/C04 apply.

**Options and choice.** Retain evidence navigation and pending literal-term tag
proposals. A general clinical chatbot invites unsupported patient-specific answers;
a full literature-discovery/ontology system requires evidence and methods beyond
this corpus. These are rejected scope expansions, not claims that the course bans them.
The [Module 1 flow][T1] supplies the RAG architecture; the biomedical restrictions
and proposal rules are our application design.

**Trade-offs.** Narrow scope gives inspectable evidence and a feasible demonstration,
but cannot establish systematic coverage or new PHOX2B mechanisms. More autonomous
claims would appear more capable while requiring validation we do not possess.

**Implementation and output.** A result must identify a source, exact quotation,
study type, qualification and pending review state. Compare atomic rows without
automatically declaring agreement or contradiction. A lookup miss says the supplied
context is insufficient; it does not say the scientific literature has no evidence.

**Completion, record and revisit.** Demonstrate one answerable question and one
out-of-scope question. Save failures as well as success. README states the user,
input, useful output and limits (R01); actual answer utility remains unproven.
Reopen scope after a documented coverage gap and an approved, usable new corpus.
Depends on D02, D10 and D13.

<a id="d02"></a>
## D02 — Select sources and preserve their authority

**Purpose and facts.** Ensure a reviewer can recover each evidence passage from a
versioned, accessible source. The current three sources are a guideline, a
retrospective clinical study and a review; article type is not population metadata.

**Options and choice.** Keep the licensed raw BioC snapshots and manifest. API-only
live retrieval would reduce snapshot maintenance but change the evidence during
experiments and require network availability. More papers could improve coverage,
but quantity alone does not fill a specified PHOX2B research gap. The [official
project instructions][TR] allow a non-FAQ original corpus; the source-version and
license contracts are our implementation.

**Trade-offs.** Snapshots enable reproducibility and offline use at the cost of
freshness. A review helps orient a question but cannot substitute for reading the
primary experiment it cites. All `population_or_model` values remain unknown until
supported annotation is added; do not infer them from a publication label.

**Implementation/output.** Keep source ID, URL, date, license, raw hash and role in
`data/manifest.json`; map retained and excluded material in the coverage reports.
A proposed addition needs a task gap, access/reuse evidence and passage-level checks.

**Validation and revisit.** Verify raw hashes, extraction coordinates, quoted text
and redistribution terms. Preserve excluded tables as a visible coverage gap (D04).
Document accessibility and reproduction under R09. Reopen when a question requires
absent primary evidence, a source changes, or reuse is unsuitable; no silent replacement.

<a id="d03"></a>
## D03 — Ingest with dlt and make the index input explicit

**Purpose and options.** Turn approved snapshots into exactly the records the app
consumes. The [dlt filesystem pipeline][TD] demonstrates loading to DuckDB. Plain
Python is simpler for a one-off file; Kestra is useful for orchestration dependencies,
retries and scheduling, but introduces a server for this small snapshot workflow.
Keep dlt → DuckDB → verified JSONL; no extra orchestration layer is justified yet.

**Trade-offs.** Replacement is easier to reason about for a complete snapshot but
reloads unchanged records. Incremental/merge ingestion needs stable keys, deletion
rules and update tests; idempotent-looking counts alone cannot prove it correct.
DuckDB is the ingestion store; it is not the vector retrieval engine.

**Implementation/output.** Run `python -m navigator ingest`. Preserve manifest/raw
hashes, source/window IDs, counts, excluded reasons, exported-file hash and corpus
fingerprint. The application reads `documents.jsonl` only after checking its receipt.

**Observed / acceptance.** Real repeated dlt/DuckDB tests reproduce the same corpus.
Require ID uniqueness, retained/excluded reconciliation, equal exported records and
stable hashes on repeat. A failed job must not leave a successful receipt for partial
new data. R06 evidence is the actual special-tool load and the consumed export,
not merely a dlt import. Reopen for updates that need tested merge semantics or a
real dependency graph. Depends on D02/D04; record commands and count deltas in D16.

<a id="d04"></a>
## D04 — Choose chunks, coordinates and heading representation

**Purpose and alternatives.** Preserve enough context to interpret a quote while
fitting the encoder. [Module 2][T2] and the overlapping-window homework supply the
patterns; BioC coordinates and heading handling are our adapters. Compare 1000/150,
750/150 and 500/100 character windows, content-only and title+content inputs.

**Observed choice.** Keep 750/150, title+content, 377 windows and zero encoder
truncations. The prior 18-configuration development comparison supports this choice.
Smaller windows fragmented useful context; larger ones did not win and could truncate.
Characters remain a construction parameter, never a tokenizer limit.

**Heading trade-off, now measured.** Adding the parent heading can disambiguate
“limitations,” but common heading terms can displace distinctive identifiers. The
new [six-variant ablation](../reports/decision-refinement/heading-ablation.json)
found heading vectors improve some comparison/limitation cases but reduce overall
reference coverage from 0.5667 to 0.5619 and MRR from 0.4695 to 0.4171. Retain the
baseline. Standalone headings still cannot serve as scientific evidence.

**Implementation/output.** Preserve unchanged `content`, source/passage offsets,
`section_heading` and IDs. Experimental `title_heading_content` changes encoder
input, not the quote. `lexical_fields` explicitly controls whether heading text is
searched. Record templates, tokenizer lengths, max length and truncation count.

**Validation/revisit.** Verify quote substring/coordinates after every representation
change. Inspect per-case gains/losses and all five answerable slices, not only the
intended improvement slice (R03). Reopen for a new encoder, source format, language
or a diagnosed lost qualification. Depends on D02/D06/D10.

<a id="d05"></a>
## D05 — Choose retrieval, storage and source filtering

**Options and baseline.** [minsearch lexical][T1], [MiniLM/vector search][T2] and
[manual RRF][T6] are demonstrated routes. Keep the measured vector baseline:
Hit@5 21/35, MRR 0.4695, reference coverage 0.5667. Lexical obtains 14/35 and 0.3524
coverage; hybrid 20/35 and 0.4952. These are development observations on provisional
labels, not universal superiority. Current output depth is 5; hybrid pool is 20.

**Trade-offs.** Lexical is cheap and inspectable but vocabulary-sensitive. Vectors
handle some paraphrases but generic MiniLM has no established biomedical advantage.
Hybrid adds complementary candidates and fusion complexity; it need not improve
the selected metric. Exact in-memory search is appropriate for 377 windows;
persistent/approximate backends taught in Module 2 add operations and tuning that
need a scale or latency requirement before adoption.

**Comparison policy.** An explicit publication filter is supported. A proposed
per-source quota ensures source presence, not relevant support: the earlier seven-
question diagnostic improved mean comparison coverage only from 0.2619 to 0.3333
and harmed one case. Do not auto-route using benchmark reference IDs. A future
named-source policy must use only the user's source selection/question.

**Implementation and checks.** Preserve filters, IDs, corpus identity and branch
ranks. Trace `candidate_k`, `top_k`, `rrf_k`, zero-based RRF and one-based display/MRR.
Measure candidate inclusion separately from final ranking, fixed pool versus larger
pool, and source presence versus required-reference coverage. Retain R03/R10 evidence;
RRF double credit remains unresolved. Reopen after diagnosed failures and a matched
D10 experiment, not for the appearance of more technologies.

<a id="d06"></a>
## D06 — Fix encoder identity and make setup explicit

**Choice and source.** Keep [Module 2][T2] SentenceTransformers/MiniLM on CPU at the
configured revision. Alternative taught encoder/storage environments remain options,
but language/domain quality and memory must be measured before switching. Normalize
both document and query embeddings; preserve row-to-document identity and dimensions.

**Implementation change.** `python -m navigator prepare-encoder` checks the existing
cache offline and encodes the active corpus. With owner approval only,
`--allow-download` can populate the pinned cache. Compose now has an `encoder-init`
job after ingestion; serving waits for it and stays offline for encoder access.
`NAVIGATOR_MODEL_CACHE` is shared explicitly. No new dependency was introduced.

**Trade-offs.** Lazy network downloads reduce setup steps but create unpredictable
first-query failures. Baking weights into the image increases rebuild/transfer size.
An explicit shared-cache initializer makes the dependency visible while retaining
an initialization step and disk use. This prepares model weights; **vectors remain
in memory and rebuild per process**, so cold-query indexing cost is still real.

**Output and validation.** `encoder-preparation.json` states ready/blocked;
`embedding-report.json` records requested/resolved revision, corpus, dimensions,
normalization, token lengths and cache location. An actual empty-cache offline check
must block without a download; an existing-cache check must pass. These were run
locally. Container initialization still needs D15 execution. Reopen for resource
pressure or domain/language changes; document setup and cold/warm latency separately (R09).

<a id="d07"></a>
## D07 — Use one complete RAG path for app and evaluation

**Purpose/options.** Implement retrieve → context → model → validation → storage →
feedback. [Module 1 component separation][T1] supports a fixed flow or an agent.
Keep the fixed flow; independently duplicated evaluator logic previously diverged
from the application at rewriting. A more autonomous loop introduces variable
context and extra calls before any benefit has been demonstrated.

**Implementation.** UI and evaluator call `rag.run_request`. `prepare_context`
records query, filters, hits, trace and hashes. Paired generator experiments freeze
this context; reuse is marked and does not count preparation calls twice. Runtime
checks bind selected evidence to code/config/corpus. The application owns metadata;
the model owns only validated answer fields.

**Output and trade-off.** Keep the original question, context, raw response, parsed
claims, source locators, timings and attempt receipt under one answer identity.
Frozen contexts improve causal comparison but are a diagnostic control; they are
not another freshly executed retrieval. Hash enforcement improves provenance but
requires new generation evidence after code changes.

**Completion/revisit.** Mocked parity/failure tests pass; they cannot close R02.
The required next proof is a real UI-generated answer through storage, export,
feedback and monitoring, plus unavailable-model/retrieval/store failures. Record
all artifacts and their exact version. Reopen if a real research task requires
multiple tool calls (D09), with a controlled baseline.

<a id="d08"></a>
## D08 — Compare local models, prompts and context policy

**Options and choice.** [2024 Phi3 Chat Completions][TL] and [Gemma 2B homework][TG]
are permitted candidates; `phi3`/`evidence_first` remains an unselected candidate.
The installed Gemma 3 cannot enter solely because a report predicts better JSON.
Paid models violate C02. Compare `concise` and `evidence_first` on identical evidence.

**Trade-offs.** Small local models remove supplier billing but may lose instruction
following, completeness or speed. Strict JSON/quotes catch broken output, not false
interpretations. Relaxing citations to improve parse rate would damage the product.
A shorter prompt/context may fit better while omitting necessary qualifications;
a larger token budget can increase latency without fixing reasoning.

**Implementation/output.** After approved setup, record installed digests and run
the six-slice pilot before a full one-model × two-prompt development comparison.
Add a second taught model only if the first comparison or diagnosed quality need
justifies its setup and compute. Keep
request text, raw output, schema result, claims, source support, complete-answer
review, usage and stage timings. Existing defaults (900 output tokens, temperature
0, 120-second timeout, no retries) are provisional settings, not measured optima.

**Failure-driven refinements.** JSON object mode is now requested as a documented
Ollama API adapter, with the same strict validation. Its real-model benefit remains
unmeasured; an explicit `json_mode: false` candidate permits comparison. For overflow,
measure actual model input limits and retained
references before trimming. For wrong meaning with valid quotes, adjust model/
prompt or scope; do not weaken the judge. No model/prompt is promoted as a measured
winner from these software checks.

**Completion/revisit.** D11 selects only from actual comparisons and applies the
recorded configuration (R04). If all candidates fail the task, report failure and
reopen scope or an owner-approved constraint; relative best does not mean adequate.

<a id="d09"></a>
## D09 — Add rewriting or an agent only for diagnosed need

**Taught options.** [Function calling][TF] and the [agent loop][TA] demonstrate
model-selected reformulated searches and multiple calls. This project adapts that
to one explicit local reformulation with ID/negation guards. It does not establish
Phi3 tool-calling capability or implement the full taught loop.

**Choice/trade-off.** Keep rewriting disabled pending a real experiment. It may help
paraphrases but can change identifiers, scope, comparison intent or caveats, while
adding latency even on failure. Fixed original search is simpler and preserves
intent. An unbounded loop makes costs/context hard to isolate; reject it here.

**Implementation/output.** Save original question, proposed query, parsed status,
identifier checks, attempt and fallback reason. Malformed output, invalid changes
and provider failure use the original query. Guards are necessary but do not prove
semantic equivalence: a reviewing agent checks both formulations explicitly.

**Acceptance and revisit.** Run the same development questions with and without
rewriting; retain all harm cases, original/new ranks, reference coverage and added
latency. Promote only if documented gains justify harms for the actual task; the
current code alone does not prove R12 or benefit. Evaluate answer effects after
retrieval gains. Reopen for observed paraphrase failures, keeping D10/D11 isolation.

<a id="d10"></a>
## D10 — Measure retrieval with references that match the task

**Options and choice.** [Module 4][T4] supplies question generation, relevance metrics
and comparisons. Use 60 provisional agent-authored questions, six slices, 42 for
development and 18 for final testing. Thirteen exposed older questions remain
regression data. This size/split is our experiment design, not a course requirement
or a statistically established sample size.

**Trade-offs.** Synthetic/agent questions are inexpensive and source-traceable but
can mirror source phrasing and miss real research needs. One relevant ID is easy
to score but insufficient for comparison questions; enumerate required reference
quotes and all containing windows without treating overlaps as independent evidence.
Agent review improves consistency but does not supply expert validity.

**Implementation/output.** Record question ID, slice, split, answerability, evidence
quotes, acceptable IDs, required facts/qualifications and absence reason. Validate
quote anchors and keep semantic siblings in one split. Preserve per-question ranks,
Hit/MRR, reference coverage, fully covered count and explicit denominators. Do not
score absent-evidence cases as retrieval misses with fabricated reference IDs.

**Observed weakness and acceptance.** The baseline fully covers 18/35 answerable
development questions and 0/7 comparisons. Diagnose absent source, excluded text,
missing label, missed candidate or low rank before tuning. Review alternative hits
before declaring them irrelevant. If labels change, version them and rescore every
candidate fairly; never edit references solely to make a chosen method win (R03).
Reopen on new use cases/corpus or label defects; preserve final-set exposure history.

<a id="d11"></a>
## D11 — Review complete answers and bind selection to evidence

**Choice and taught basis.** Use [Module 4 paired evaluation][T4], with our five-part
review: structure, quote integrity, entailment, completeness and appropriate abstention.
Compare alternatives on frozen evidence. Manual agent review avoids another model
setup; automatic judging scales review but adds calls and may prefer its own model.
Neither route constitutes biomedical expert validation (C03).

**Implementation and trade-offs.** Automatic judging requires five known-error
fixtures and a matched judge digest/instruction/settings contract. Passing fixtures
only establishes those fixtures. A fixed judge reduces variability but shares Phi3
with one candidate; an independent agent inspects disagreements, every serious
failure and a declared sample of successes. Blind candidate names where practicable.
Cross-judging with both models doubles calls and agreement still is not truth; use
it only as a documented disagreement diagnostic, not an automatic requirement.

**Output/selection.** Keep result/review hashes, claim support, required facts and
qualifiers, abstention reasons, per-slice denominators and raw receipts. Complete
current-code development runs can nominate a provisional winner by acceptable
answers, then unsupported claims/errors, latency and stable tie-breaking. Explicit
`--apply` writes the manifest; runtime verifies it. Eligibility requires at least
one acceptable answerable response after whole-answer review and no critical or
unsupported-claim failure. A nonzero aggregate from refusals alone is insufficient.
These conditions are not a product-quality threshold or submission-ready declaration.

**Reassessment correction.** Selection now matches complete frozen reference
requirements to the active question bank, reconstructs context identity from the
actual source fields and query, and checks each request/raw-output receipt against
the reviewed answer. SDK fixtures cannot supply live selection evidence. Calibration
paths are portable and their backing files are rechecked at runtime. Old incomplete
artifacts must be regenerated; hashes are consistency checks, not proof against
someone deliberately rewriting the entire evidence set.

**Acceptance/revisit.** A correct but incomplete fragment fails completeness. Safe
abstention after poor retrieval still fails an answerable end-to-end task. Use known
reference context to separate retrieval from generation failures; do not replace
benchmark results with this easier diagnostic. Run the full final split only after
selection. R04 needs evaluated alternatives and the selected approach in use; two
models, 60 questions and a calibrated judge are our safeguards, not official mandates.

<a id="d12"></a>
## D12 — Improve one cause at a time and retain negative results

**Decision rule.** Fix broken flow/measurement before adding bonus-oriented components.
The [Module 4 comparisons][T4] and [optional RRF lesson][T6] support controlled
experiments. A larger candidate pool, heading representation and reranking are
different interventions; changing all at once prevents attribution.

**Observed example.** The heading experiment held corpus, development questions,
output depth and baseline parameters fixed. Heading vectors gained COM-05, COM-06
and LIM-02 coverage but lost PAR-06 and EXA-04. Heading hybrid improved its own
baseline MRR yet still lost to the selected vector coverage. No candidate beat the
predeclared overall rule; retain the incumbent and record the negative outcome.
This is a completed decision, not an unfinished recommendation.

**Next alternatives and trade-offs.** Audit labels/exclusions for known misses;
then test explicit named-source comparisons, a bounded boost grid or rewriting
against the incumbent. More candidates can improve recall but consume context,
latency and judge effort. A new LLM reranker is not permitted merely because judging
was taught for answers. Manual RRF is demonstrated; scoring it twice is unresolved.

**Implementation/acceptance.** Save hypothesis, exact change, invariant corpus/split,
configurations, candidate/final ranks, per-case regressions, resource measurements
and selection rule before execution. A selected improvement must be checked for
answer effects and reflected in application configuration. No test-set tuning,
hidden failures or automatic point claim. Depends on D04–D11; document evidence for
R03/04 and any applicable practice criterion separately.

<a id="d13"></a>
## D13 — Make the result inspectable and keep exports faithful

**Options/choice.** [Module 5 Streamlit][T5] provides rapid forms, tables and feedback;
an API or a more elaborate taught interface would add work without improving the
current evidence inspection task. Keep separate evidence-preview and LLM-answer
modes, with source filtering and per-session result state.

**Trade-offs.** Preview is useful before local models are available, but returning
passages is not a generated answer. Atomic rows preserve provenance at the cost of
longer tables. Literal-term proposals are transparent but miss synonyms and should
not be advertised as scientific discovery. Unknown context is visible, not filled
with plausible model metadata.

**Implementation/output.** Show answer ID, mode, source version, claims, quotes and
limitations. CSV/JSON exports preserve source and review state; spreadsheet-formula
escaping protects CSV without rewriting the JSON evidence. A proposal always says
`PROPOSED_PENDING_HUMAN_REVIEW` with no registry action.

**Reassessment correction.** Exports revalidate persisted claims and reject empty
quotes or a preview record populated with claims. License/language accompany the
source rows. The actual preview download was checked against all five stored windows;
this does not establish a generated-answer download.

**Validation/revisit.** Browser-download a real answer and compare saved bytes/IDs
with the shown result; vote on that answer and recover it in monitoring. AppTest
checks software behavior but cannot prove a browser download or genuine model output.
Test malformed payload, session isolation and storage failure. Screenshots must
show actual UI, with preview/QA labels retained (R05). Reopen for observed reviewer
confusion or a justified research interaction, not cosmetic bonus hunting.

<a id="d14"></a>
## D14 — Monitor truthful denominators and feedback identity

**Options/choice.** Keep [Module 5][T5] Streamlit/pandas charts and PostgreSQL, with
explicit JSONL for development. Grafana is taught but adds provisioning overhead;
its name is not required to satisfy monitoring. Five meaningful charts meet the
rubric's chart count; seven charts have no automatic score advantage.

**Implementation and output.** Preserve one answer ID, `traffic_origin` and mode
through storage/feedback. Both storage adapters now reject an origin mismatch.
Dashboard aggregation excludes mismatches even under `all` and reports their count;
legacy unknown records are not silently classified as user activity. No migration
or historical relabeling was performed.

**Trade-offs/definitions.** User-only default avoids confusing QA with research use
but can initially be empty. Select `qa` explicitly for a demo; do not label agent
runs `user` to fill a chart. Volume/outcomes use stored requests; feedback uses
unique rated answers in scope; passage count is not relevance; generation timing
excludes retrieval/storage; tokens include only observed counts. Local API cost zero
does not mean electricity zero, and missing usage must remain null.

**Acceptance/revisit.** New regression tests cover mismatched all-scope votes and
adapter rejection. PostgreSQL checks use a mock; live transaction/restart proof
awaits D15. Add a chart only for a specific operational question with a stated data
source and denominator (R07). Reopen for multi-user vote policies or incomplete
telemetry; document any counting-policy change before comparing periods.

<a id="d15"></a>
## D15 — Prove a complete reproducible stack

**Options/choice.** Keep native local development and a complete Compose release
path using [Module 5][T5] and [2024 Ollama Compose][TC]. Native Mac inference may be
faster, but a local run does not establish container behavior. Exact images and
locks reduce drift; they do not prove compatibility on every machine.

**Implementation.** Compose wires dlt ingestion → encoder initialization → app,
Ollama → course-model initialization → app, and healthy PostgreSQL → app. Named
volumes preserve models/artifacts/database; UI binds to loopback. Encoder access
is offline during serving. Each initializer fails visibly. Selected-generation
reports accompany the build because runtime verifies their hashes.

**Trade-offs.** Initialization downloads and disk space are explicit. CPU container
inference may be slower than native acceleration; do not promise Mac GPU access.
Model tags remain mutable even when the server image is pinned: record observed
weight digests and reject mismatch with a selected release. Baking or pinning all
weights is a later reproducibility option requiring storage/transfer evidence.

**Acceptance/output.** After the required Docker setup approval: use an isolated Compose
project, follow only README, save build/service/init logs, make a real answer, check
DB feedback and exports, restart without deleting volumes, verify persistence,
then test model/DB failure and recovery. Save versions, architecture, digests and
cold/warm timings. This has not run. R08's wording concerns the full Compose setup;
R09 also requires working reproduction. Our stricter rehearsal is a quality gate,
not an invented official scoring tier. Reopen after measured incompatibility.

<a id="d16"></a>
## D16 — Make the evidence easy to review without concealing gaps

**Choice/source.** Follow the [official documentation guidance][TR]: explain the
problem, data, operation and criterion evidence for someone who did not take the
course. A concise README with linked detailed reports is better than either an
unstructured audit dump or an unsupported polished success story.

**Trade-offs.** More detail enables audit but can bury the working path. Keep a
short capability/status table near the top, the runnable path, actual result table
and criterion links. Put long decision records here. Preserve visible live-model
and container blockers until evidence closes them; moving them out of view does
not improve readiness.

**Implementation/output.** Every claimed capability links code, executed result and
reproduction command for the same version. Separate course requirement, project
safeguard, observed result and proposed experiment. A real successful answer example
and screenshot are pending; no fixture or preview may impersonate one. Keep
negative ablations and explicit label limitations alongside the positive result.

**Acceptance/revisit.** Check relative links/anchors, configuration/evidence hashes,
source preservation and exact rubric arithmetic. Past project READMEs provide
presentation ideas; public scores without per-criterion comments or confirmed
submitted commits cannot prove that a particular tool earned points. Reopen when
reviewers cannot find evidence or when implementation changes make a claim stale.
Depends on all preceding decisions, especially D11/D15.

<a id="d17"></a>
## D17 — Separate technical readiness from release and grading

**Facts/options.** Nine core criteria total 18; three named practices, cloud and
up to three discretionary points bring the rubric maximum to 26. Peer-review points
are separate. The official course permits external tools, but C01/C02 still govern
this project. No verified free, taught whole-stack cloud route is presently selected.

**Choice and trade-offs.** Close live flow, output comparison and reproduction
before pursuing optional points. Cloud adds operations and possible cost; RRF double
credit and discretionary extras are reviewer decisions. The attached report's
KB-without-LLM partial point is not the rubric's stated one-point LLM-only tier.
Do not manufacture an intermediate official rule or guarantee 26/26.

**Implementation/output.** Maintain a criterion→code→result→command matrix and
release readiness checklist. Current missing five core points (R02 +2, R04 +2,
R09 +1 under the earlier evidence assessment) remain unproven by unit tests.
After technical gates pass, the owner controls a fixed commit, accessible reviewer
repository, publication and actual submission. Verify cohort logistics and reuse
eligibility at that time; historical/general links differ and do not establish a
personal submission history.

**Completion/revisit.** Technical acceptance, research usefulness, public release,
course eligibility and awarded score are separate states. Record completed peer
reviews only after actual submission/review actions. No external action is authorized
by this decision record. Reopen after new primary course rules, an approved constraint
change or new execution evidence; rescore criterion by criterion with those artifacts.

## Copy-ready decision / experiment record

```yaml
decision_id: D12-example
status: PROPOSED_NOT_EXECUTED
requirement: improve named-source evidence coverage without losing exact-ID retrieval
constraints: [C01, C03, C06]
course_source: exact lesson/notebook permalink and location
adaptation: explain the project-specific change; no invented instructor rationale
missing_facts: [which candidate/reference failure causes the miss]
baseline: {config_id: REQUIRED, corpus_id: REQUIRED, code_id: REQUIRED}
options:
  - name: incumbent
    benefit: measured baseline
    cost: known comparison coverage gaps
  - name: candidate
    benefit: expected, not measured
    cost: expected latency, context and regression risks
experiment:
  split: tuning
  question_ids: REQUIRED
  invariant_fields: [corpus, labels, final_cutoff]
  isolated_change: REQUIRED
  selection_rule: declare before running
  cases: REQUIRED_AFTER_EXECUTION
  raw_results: REQUIRED_AFTER_EXECUTION
  metrics: {numerators: REQUIRED, denominators: REQUIRED, uncertainty: provisional_labels}
  timing: {setup_seconds: null, query_seconds: null, generation_seconds: null}
rejected_options_and_reasons: REQUIRED_AFTER_REVIEW
selected_configuration: NONE_UNTIL_REVIEWED
application_manifest: NONE_UNTIL_APPLIED
revisit_trigger: specify a measurable failure or changed constraint
rubric_evidence: criterion, code, result and reproduction command
```

The completed heading ablation in D04/D12 is the concrete example: six declared
alternatives, unchanged corpus/configuration, preserved gains and regressions,
and a reasoned rejection. Live-model outcomes are deliberately absent until run.

[T1]: https://github.com/DataTalksClub/llm-zoomcamp/blob/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/01-agentic-rag/code/rag_helper.py
[T2]: https://github.com/DataTalksClub/llm-zoomcamp/tree/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/02-vector-search
[TD]: https://github.com/DataTalksClub/llm-zoomcamp/blob/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/cohorts/2026/workshops/dlt/code/filesystem_pipeline.py
[T4]: https://github.com/DataTalksClub/llm-zoomcamp/tree/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/04-evaluation
[T5]: https://github.com/DataTalksClub/llm-zoomcamp/tree/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/05-monitoring/code
[T6]: https://github.com/DataTalksClub/llm-zoomcamp/blob/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/06-best-practices/lessons/03-reranking.md
[TL]: https://github.com/DataTalksClub/llm-zoomcamp/blob/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/cohorts/2024/02-open-source/qa_faq.py
[TG]: https://github.com/DataTalksClub/llm-zoomcamp/blob/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/cohorts/2024/02-open-source/homework.md
[TF]: https://github.com/DataTalksClub/llm-zoomcamp/blob/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/01-agentic-rag/lessons/13-function-calling.md
[TA]: https://github.com/DataTalksClub/llm-zoomcamp/blob/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/01-agentic-rag/lessons/14-agentic-loop.md
[TC]: https://github.com/DataTalksClub/llm-zoomcamp/blob/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/cohorts/2024/02-open-source/docker-compose.yaml
[TR]: https://github.com/DataTalksClub/llm-zoomcamp/blob/main/project.md

---

## Dated decision log — retained historical evidence

Some entries below describe an older corpus, earlier selection, or pending work
that has since been addressed. Use D01–D17 above and current configuration for
present decisions. The entries are preserved rather than retroactively rewritten.

### Previous remediation summary

These choices supersede the historical baseline below. Implementation adaptations
are original project work, not additional instructor claims.

| Decision | Evidence and choice | Rejected alternative / trade-off | Revisit trigger |
|---|---|---|---|
| Evidence granularity | Heading-only passages excluded, heading retained as metadata | Indexing a heading produced false evidence candidates in the real browser | A source format contains substantive information in a heading; audit separately |
| Windows | 750 characters / 150 overlap | 1000 risked truncation; 500 fragmented evidence and did not win | New corpus, language or model length constraints |
| Retrieval | Vector with title+content on provisional v2 development labels | Text, content-only and RRF hybrid lost the predeclared reference-coverage comparison | Representative new labels or real error analysis demonstrates a different winner |
| RRF | Keep the taught zero-based implementation and rank traces as an evaluated alternative | Do not add an untaught reranker or force inferior runtime hybrid for a point | New controlled experiment or an official scoring clarification |
| Local provider | Course 2024 Ollama/Phi3 and Gemma 2B candidates | Paid API violates the chosen zero-payment constraint; installed Gemma 3 lacks taught-use evidence | Approved constraint change or measured course-model comparison |
| Answer quality | Require all reference facts and qualifications as well as supported claims | Quote validity alone misses omissions and semantic errors | Revised research task and explicitly versioned reference requirements |
| Query rewrite | One local call, explicit fallback, disabled pending experiment | Unbounded agent loop adds changing context/cost without demonstrated benefit | Intent-preserving development gains justify activation |
| Research tables | Atomic source claims and literal quote-term proposals pending review | Automatic scientific relations/registry activation exceed the available evidence | Separate human research governance, outside this release |
| Packaging | Full Compose including Ollama and initialization, images pinned by digest | Native Mac path may be faster, but does not prove complete container reproduction | Actual CPU/container resource measurements |

Every model/rewrite/judge experiment records its status. Generation selection,
scientific validation and complete container runtime are still open.

### Earlier corpus and 13-question bank

#### Earlier decision register

All choices below are project adaptations of the cited course methods. Numerical
defaults are provisional experiment settings, not validated thresholds or lecturer
recommendations for CCHS.

| ID / stages | Selected approach | Alternatives and tradeoffs | Validation / revisit trigger |
|---|---|---|---|
| ADR01 / D01–02 | Evidence navigation on licensed English seed literature | Full LBD/ontology system requires additional scientific labels and methods; multilingual search adds a separate evaluation burden | Researcher utility pilot; expand scope only after evidence layer works |
| ADR02 / D03 | dlt to DuckDB, exporting exact app records | Plain Python ingestion has less setup; Kestra adds a server without a demonstrated dependency need | Verify counts, IDs, export equality and repeat ingestion |
| ADR03 / D04 | 1000-character windows, 150 overlap inside each retained passage | Larger windows preserve context but dilute retrieval and risk encoder truncation; smaller windows may sever meaning | Record truncated count and inspect retrieval/context errors; never tune on final test |
| ADR04 / D05–06 | Hybrid selected over measured lexical and vector baselines | Same tuning coverage as lexical with higher MRR; adds encoder setup, memory and slower queries | [Selection evidence](../reports/config-selection.json); quality labels remain provisional, and test Hit@5 is 2/4 |
| ADR05 / D07–09 | Fixed RAG with two prompt variants and strict citation/quote validation | Agent/rewrite loop adds calls and moving context; unnecessary before a measured retrieval failure | Live paired prompt results and human support judgments; no fabricated winner |
| ADR06 / D13–14 | Streamlit UI/dashboard and PostgreSQL feedback | Grafana is taught but adds a service; local JSONL is explicitly a development adapter | UI reruns, duplicate votes, FK integrity, restart and real chart data |
| ADR07 / D15 | Compose plus complete dependency locks | Local setup starts with fewer services but cannot prove the complete container criterion | Clean build/start, ingestion completion, DB readiness and persistence |
| ADR08 / D16–17 | Private GitHub development repository | Public access is needed for the course reviewer; user requested private development | Owner must approve a later visibility/access change; no automatic submission |

For new decisions use: problem/requirement, missing facts, constraints, exact
course source, candidate configurations, expected tradeoffs, chosen baseline,
experiment, observed per-case results, rejected options, active config fingerprint,
README evidence link and a reversal condition. Do not label expectations as results.

### ADR04 execution update — 2026-09-05

At fixed top-5 depth, prioritize tuning Hit@5, then MRR. Title+content hybrid
obtained 5/7 and 0.5476 versus lexical 5/7 and 0.2000, and vector 4/7 and 0.3929.
Content-only encoding reduced truncated inputs from 8 to 4 but hybrid MRR fell
to 0.3500. Combining content-only vectors with title/section/content boosts
0.2/0/3 reduced hybrid coverage to 4/7. Both ablations were rejected. These are
observed development results, not lecturer recommendations or validated CCHS defaults.

Keep title+content, CPU MiniLM at the pinned revision, 384 dimensions, L2
normalization, candidate depth 20, RRF constant 50 with zero-based ranks and
top-5 output. Eight of 411 encoder inputs still truncate at 256 tokens. The
direct exact-vector diagnostic preserved row IDs and reproduced library rankings;
no mapping defect was found. Full passages remain available to the answer context
and reviewer even when their embedding input truncates.

The active config fingerprint is
`b7b7e0e80c62cc1d72c7e1aaacbb14dc959b4dff58e07cb40a20be088a88cdbb`.
The subsequent selected-only test obtained 2/4 Hit@5 and 0.3750 MRR@5; do not
change configuration using these exposed test outcomes and call the rerun unseen.
Revisit using reviewed labels and a new documented tuning experiment. A future
scientific quality claim requires independently reviewed test questions. No
unmeasured rewriting/agent advantage is inferred from the failures.

The default Docker build now includes vector dependencies, and the local README
installs the vector lock. This is an original packaging correction to keep the
documented runtime consistent with the selected configuration; it does not prove
a container build or add a new retrieval method.

### ADR09 — Examiner remediation, 2026-09-06

Reject additional model fields and copy only validated answer content. Application
identity, sources and usage remain authoritative. This uses Python validation around
the Module 1 Responses flow; no new framework. Regression tests reproduce the prior
overwrite and require rejection. Store creation is excluded from the retriever cache
to avoid crossing runtime environments.

Use five measured core charts plus an optional provider-token chart. Passage count
is a context-size diagnostic, not answer quality. Origins are explicit and legacy
records are unclassified; no fabricated provider traffic is needed. This adapts the
Module 5 pandas/Streamlit monitoring approach.

The predeclared 12-case Homework 4 RRF grid retained the incumbent: candidate depth
20, zero-based k=50. No new independent quality claim is made. Tuning labels need
researcher review; the packet makes both reference and retrieved passages inspectable.

Answer selection remains pending. The new workflow requires a real paired run,
reviewer kind, per-claim support, abstention and relevance judgments, validated
artifact hashes, and a recorded choice. No default prompt is called a measured winner.
See [remediation and acceptance evidence](review-remediation.md).

### ADR10 — Core evidence follows the application's flow

Use one Module 1-style request composition for the UI and evaluator. Freeze
contexts when isolating generator/prompt effects, preserve their provenance and
count preparation once. Duplicated app/evaluator logic already diverged at
rewriting. Tests now verify parity and failure behavior; SDK fixtures cannot
establish local-model quality.

Keep the existing retrieval configuration while closing R02/R04/R09. Do not
enable rewriting or another comparison route as an unmeasured side effect. This
retains known retrieval weaknesses until a separate experiment justifies change.
Reopen if live answer evidence shows retrieval prevents the intended task.

Use Module 4 comparisons with six-slice pilots, calibrated judging and complete
development selection. Hashes, CLI statuses, selection manifests and durable call
files are project engineering adaptations, not additional taught algorithms.
Re-evaluate after relevant code/configuration/corpus changes. Documentation-only
changes do not change the runtime Python-code hash; held-out results never select.

### ADR11 — Apply the external notes without turning assumptions into requirements

**Requirement and choice.** Close the real R02/R04 evidence gap before optional
bonuses. Use the existing taught Phi3 route with two prompts and explicit assistant
reviews. Reduce Compose's initial model download to Phi3. Gemma remains a permitted
later comparison, not a prerequisite for this experiment.

**Trade-off.** This reduces setup, generation and review work, while providing no
claim about which model family is best. Pilot six development questions (maximum
12 calls), then run all 42 development questions (maximum 84 calls). The sizes are
project choices. Save every output and review; never reuse the exposed pilot as
independent test evidence. A second model is justified by a diagnosed quality need,
not by the assumption that the rubric requires a 2×2 grid.

**Robustness.** Request JSON object mode through the existing SDK, retain all source
validation, and record the mode/timeout in receipts. Permit a validated finite
positive timeout override; equivalent numeric values retain their config hash.
Keep 900 output tokens, five evidence passages and uncapped exact-quote lengths
until a measured experiment supports a change. Reducing output allowance cannot
be claimed to prevent truncation; it may cause truncation sooner.

**Failure accounting.** A completed malformed response is an observed unsuccessful
answer, not an interrupted experiment. Continue the paired comparison, count the
error and require a review. Infrastructure/provider failures still stop. Selection
checks request/raw-response integrity and confirms an error-labeled raw response
really fails validation. It still refuses incomplete, mismatched or zero-quality
comparisons. This change improves measurement, not a model's scientific accuracy.

**Setup/monitoring.** Preflight records real metadata without pulling weights. Keep
architecture capacity distinct from loaded context. The dashboard starts in the
session's origin so QA activity is visible and remains labeled QA. Do not mix
origins merely to create a fuller-looking chart.

**Evidence and revisit.** See the [Claude response](../reports/claude-remediation/response.en.md),
[failure diagnosis](../reports/claude-remediation/retrieval-misses.json) and
[check results](../reports/checks.json). Real model compatibility, answer quality and
Compose behavior remain to be demonstrated after setup approval. Revisit JSON mode,
timeout, context policy or model choice based on saved failures and controlled
comparisons; never promote a new default merely from fixture success.

### ADR12 — Approved course-model setup and Phase 0 preflight (2026-09-06)

**Owner decision (10:40 Asia/Jerusalem).** The owner authorized downloading the two
taught local models. `ollama pull phi3` completed at 10:47 and `ollama pull gemma:2b`
at 10:51, both with exit code 0. Installed digests: `phi3:latest`
`4f222292793889a9a40a020799cfd28d53f3e01af25d48e06c5e708610fc47e9` (3.8B, Q4_0,
architecture context 131072, RoPE original 4096); `gemma:2b`
`b50d6c999e592ae4f79acae23b4feaefbdfceaa7cd366df2610e3072c052a160` (2.51B parameters,
Q4_0, architecture context 8192). The pre-existing `gemma3:12b` stays outside the
course boundary (C01/C02) unless the owner opens that gate. Docker remains absent;
its installation is still an owner action.

**Preflight record.** `check-runtime` reports `RUNTIME_METADATA_READY`;
`prepare-encoder` (offline) reports `ENCODER_READY` at the pinned revision with zero
truncated inputs; the suite is 98/98. The combined record is
[`reports/final/phase0/environment.json`](../reports/final/phase0/environment.json).
Nothing was loaded in Ollama at preflight, so the effective context window is still
unobserved: the first generation step must read `/api/ps` after its first call, and
Compose should set `OLLAMA_CONTEXT_LENGTH` explicitly rather than rely on a default.

**Correction.** `ollama/ollama:0.31.1` is the 30 June 2026 release, and CLI and server
match at 0.31.1; the external note calling it a 2024 image is withdrawn. The digest
pin stays.

**Next.** Six-question two-prompt pilot on `phi3` (`evaluate-answers --max-questions 6`),
reviews, then the full development run and `select-generation`. No generation call
was made in this step; no commit, push, publication or submission occurred.

### ADR13 — Enforce the whole-answer contract, then test coverage instructions

Iteration 001 makes the existing whole-answer veto mandatory in selection and
runtime evidence, retaining source-based assistant review. Iteration 002 separates
a completed token-limited response from a service outage: it stays a failed answer
and the planned comparison continues without retry or a budget increase.

The next prompt-only candidate, `coverage_first`, explicitly asks for each requested
fact and qualification, exact copied citations, and no invented premise in
limitations. It is based on Module 1 prompt composition and Module 4 comparisons
([course sources](course-sources.md)); the wording is our project adaptation.
The longer instructions may increase input cost/time or distract a small model.
Keeping the short prompt, changing models, increasing the output budget and
changing retrieval are alternatives; isolate those only after this same-context
comparison. The active app prompt stays `evidence_first` until full measured
evidence justifies selection. A pilot improvement alone is insufficient.

Evidence and predeclared keep/reject rules live under
[goal-loop iterations](../reports/goal-loop/iterations/). Official points remain
unknown; this does not establish R04's highest tier or useful answer quality.

### ADR14 — Reject unsuccessful alternatives; isolate message composition

The completed 14-call Phi3 pilot and 14-call Gemma 2B pilot each yielded 0/7
acceptable responses for both tested prompts. Gemma could copy quotations while
misattributing the publication and deriving unsupported claims. Both candidates
were rejected; a valid quote is not evidence of a valid conclusion. Failed
outputs and source-based whole-answer judgments remain in the iteration records.

The `course_user` candidate retains the incumbent evidence-first wording and all
source fields, but uses the single-user-message QUESTION/CONTEXT layout in the
2024 `qa_faq.py` example. It may improve question salience for the local model;
it also reduces separation between instructions and untrusted context. The output
validator and all semantic acceptance rules remain unchanged. A focused six-call
diagnostic tests two questions whose complete reference facts are retrieved and
one unsupported-premise question. It cannot establish six-slice coverage, a
selected winner or final-set performance. Preserve the incumbent unless broader
evidence meets the whole contract; reject the layout if it introduces critical
source/meaning/ownership failures.

### ADR15 — Separate citation transport, output mode and answer meaning

**Evidence.** Iterations 006–010 tested output-shape instructions, known-reference
context, plain text serialization, short citation labels and JSON object mode.
See [per-experiment decisions and results](release-status.md#release-blockers-and-completion-rule).
None passed the complete-answer contract. Even reference-only context did not
produce complete supported answers for the two diagnostic questions, so retrieval
noise alone does not explain the failures. Turning JSON mode off produced the same
decoded JSON in all six corresponding comparisons.

**Choice and implementation.** Preserve the incumbent. Candidate `short_ids`
replaces long evidence IDs with request-local labels only in the model exchange.
The application restores canonical IDs before the unchanged quote validator and
exports, and selection reconstructs that exact mapping. Unknown labels, wrong
quotes and invented source fields are rejected. This is our context/ID adapter
based on Modules 1/4, not a course-taught biomedical method or a selected winner.

**Alternatives and trade-offs.** Full IDs need no alias map but burden exact
copying; short IDs add a request-scoping contract. Plain text is easier to read but
did not prevent long-hash/ID confusion. Repairing model quotes or fuzzy-matching
invented IDs would obscure errors and is rejected. More output instructions
increased invalid outputs in the tested pilots. Valid JSON or a valid quote still
cannot establish the meaning or completeness of an answer.

**Verification and revisit.** Four alias tests cover canonical export identity,
unknown/foreign labels, per-request scope and selection tampering. All actual
responses have separate primary and whole-answer reviews; malformed responses
remain counted. Reopen context presentation by isolating redundant transport
metadata from needed scientific context, or reconsider a taught model with exact
implementation provenance and any required download approval. Do not alter facts,
answerability or final-test exposure to accommodate the model. A successful small
pilot would only justify broader development evidence, never immediate promotion.

### ADR16 — Prepare an isolated reproduction rehearsal

The existing native app occupies the Compose default port. Parameterizing only
the host port avoids stopping it, while preserving loopback access, container port
8501, the six services and persistent volumes. Keeping the fixed occupied port
would obstruct the rehearsal; publishing to all network interfaces is unnecessary.
The small packaging change passed a YAML parse and explicit service/volume/port
checks, but Docker interpolation and actual execution are pending. No runtime
generation setting or active quality selection changed.

The [rehearsal plan](../reports/goal-loop/compose-rehearsal-plan.md) records the
installation/download scope, disk observation, unmeasured resource needs, current
Linux CUDA dependencies, browser export checks, QA accounting and restart proof.
Docker is absent and installation approval remains required by the owner. This
closes a preparation defect; it does not award R08/R09 points or establish a clean
reproduction. Revisit packaging only from an observed build/runtime failure or a
separately validated CPU dependency resolution.


### ADR17 — Diagnose model formatting burden without hiding semantic errors

**Problem and evidence.** Compact metadata reduced prompt size but left all six
paired answers unacceptable (012). Ordinary prose recovered the count and period
on DIR-02 (013); the other cases still contained unsupported or misplaced facts.
This supports a formatting-burden hypothesis for those cases, not a general model
quality claim. The 2024 `qa_faq.py` uses ordinary question/context prose; Module 1
`rag_helper.py` projects source fields into context. Our controlled diagnostics
change only their declared interface and preserve the ordinary retrieved passages.

**Alternatives and trade-offs.** A second formatting turn (014), informed by taught
message/context preservation and staged synthesis, adds latency and can propagate
wrong claims. It produced 0/2 complete answerable outputs and one safe nonanswer,
so we rejected integration. A source-attachment prototype (015) asks for claim
text and an E-label, then joins the original source window by that exact ID, an
application of Module 4's document-ID lookup. The model cannot supply quotations,
URLs or versions. This reduces copying but attaches a broader window; source
identity/quotation consistency cannot certify the claim's meaning. The existing
canonical answer validator and full semantic/completeness review still apply.
If integrated later, quote scope and application ownership must be explicit in
exports, and term proposals must not imply that every term in the window supports
the specific claim. Neither prototype is the production request path.

**Result and decision.** Phi3's source-attachment prototype gave one complete
supported count/period answer, an incomplete unnecessary refusal for study design,
and an unsafe nonanswer that strengthened uncertainty. Gemma 2B (017) failed the
same interface, and more generic guidance (018) lost the Phi3 success. Keep the
incumbent. Do not combine the best answers from different failed variants into a
fictional winner. Reject fuzzy quote repair, hidden output removal and inference
from paper publication year to study period. All actual failures remain recorded.

**Verification and reopening.** See iterations 012–018 in [readiness](readiness.md).
The adapter's synthetic checks reject foreign labels and model-owned source
metadata; a true attached source with a false claim intentionally exposes the
need for semantic review. Reopen with a predeclared simpler model interface only
if required facts, scientific caveats and all visible prose remain fully judged.
A viable pilot would justify broader development comparison, not selection or R04
completion. Scientific claims and tag suggestions remain pending human review.

### ADR18 — Keep vector retrieval despite a better aggregate hybrid result

**Decision.** Iteration 016 keeps the selected vector default. On the same 35
answerable development questions, removing lexical title weight raises hybrid
full-reference coverage to 22/35 versus vector's 18/35. It also loses both DIR-07
and PAR-01 completely, and loses partial coverage on COM-02. That fails the
predeclared condition of retaining fully covered cases. The frozen labels are a
reference-coverage proxy, not an exhaustive list of all relevant passages.

**Reasoning and trade-offs.** Module 1 minsearch field boosts and Module 4 paired
retrieval evaluation justify measuring the title feature; the chosen numerical
weights are project experiment settings, not lecturer recommendations. Real branch
ranks show that RRF can favor agreement on less useful candidates over a strong
single vector hit. Increasing aggregate coverage while losing an already answerable
research question is a material trade-off. Switching to hybrid merely for a bonus
would leave that problem unresolved. Keep the same top-5, candidate-20, zero-based
RRF convention and corpus when attributing this particular experiment's effects.

**Next evidence.** A separately predeclared rank/cutoff diagnostic could test that
failure mechanism using the saved branch rankings. Do not special-case question
IDs or change active settings from a post-hoc favorable slice. Record winners and
losers, then verify answer completeness before any promotion. No additional model
calls were made by this retrieval experiment.

### ADR19 — Require useful answerable responses before generation nomination

**Defect.** An always-abstaining variant could earn a positive aggregate from the
unanswerable part of a mixed bank. The prior all-abstention test contained only
answerable questions, so it missed that path. This violates the already frozen
Goal contract; it is not a newly invented course accuracy threshold.

**Correction and alternatives.** Exclude candidates with no acceptable answerable
response from primary nomination, post-veto nomination and actual selection.
Preserve correct refusals, failed rows, all judgments and denominators. Dropping
unanswerable cases would discard a necessary safety check. Counting safe fragments
as complete or editing labels to raise the numerator is also rejected. At least
one complete supported answer is necessary for eligibility, never sufficient to
satisfy the full development, final-test, research-task or reproduction gates.

**Verification.** The old evaluator and two reproduced test failures are preserved.
After repair, nine targeted tests pass, including a supported answerable candidate
and a whole-answer veto that removes the last answerable success. The complete
suite passes 116 tests with zero skips. Recomputing 14 saved result packets under
both versions preserves all per-question judgments and metrics. Historical raw
outputs/reviews remain unchanged, including the partial pilot's obsolete sidecar
limitation. See [the comparison](../reports/goal-loop/evaluator-019-comparison.json).

**Implication and revisit.** Keep this software repair. It provides no new real
answer-quality evidence and awards no R04 points. Future candidates must still
pass semantic source review and the full protected contract. Reopen this policy
only through an explicit, reviewed change to the task's intended utility, never to
make a failed candidate appear successful.


### ADR20 — Reject smaller output and per-source workflows when complete answers fail

**Evidence.** Iteration 020 removes model-authored status/limitations and derives
only a truthful application process note. This preserves every required scientific
fact and caveat in the final claim contract; extra model fields are rejected, not
silently dropped. All three outputs parse, but source attribution, relevance and
completeness still fail. It is rejected.

Iteration 021 applies the taught source-context RAG call separately to each of the
same five windows and combines all validated atomic rows. This is our Python
workflow adaptation, not a course claim that per-source calls are superior. One
DIR-02 source call gives the complete supported count and period. Other calls
produce schema failures, irrelevant material and an unsupported study-time
assertion, so the combined answer remains rejected. PAR-01 omits electronic
records; ABS-01 has four correct empty source outputs and one irrelevant background
claim, so the final response fails abstention. All 15 source-level attempts are
reviewed and retained. Do not select just the favorable fragment afterward.

**Trade-off and next step.** Five calls per question add time and failure surfaces.
They reduce some cross-source mixing but cannot solve within-source relevance or
unsupported extrapolation. Keep the one-call incumbent. These diagnostics justify
considering a bounded model-precision experiment; they do not prove quantization
caused the failures or that a larger model would solve them. Reopen a workflow
only with a predeclared useful-output gain and no critical regression, followed
by the full development and final assessment protocol.

### ADR21 — Prepare an exact Phi3 precision variant without changing the default

The [feasibility report](../reports/goal-loop/model-feasibility.md) compares the
existing Phi3 Q4 path with an exact Q8 Mini tag and the actually taught FLAN-T5 XL
and Mistral-7B alternatives. Q8 uses the current provider/libraries and adds about
4.1 GB of weights; memory, latency and semantic benefit remain unmeasured. The
public registry records match on template and stop-parameter content. The installed
model's architecture and context allocation must still be verified after an
approved download; catalog window labels alone are insufficient.

This is our application of the 2024 precision/resource trade-off, demonstrated
through Mistral's quantized loading, to the already taught Phi3/Ollama route. The
exact Q8 tag is not claimed to appear in the lecture. The provider allowlist adds
only that tag; it does not permit arbitrary variants, downloads, changed weights
under a selected digest or a paid fallback. The active configuration stays Q4.
Existing model-identity tests now cover both alias forms, digest mismatch and a
missing requested model; the full 116-test suite passes.

The [predeclared plan](../reports/goal-loop/iterations/022-phi3-precision-pilot.json)
compares evidence_first/schema_first on three development questions against the
preserved matching Q4 outputs, without retries or changed references. It has made
zero calls and needs explicit download authorization. A failed candidate stays
rejected; a successful pilot only justifies broader development evidence. No
point or readiness status changes merely because the new tag is accepted by the
provider. Revisit this choice if installed serving metadata prevents a controlled
comparison, resources are unsuitable or the measured answers do not improve.

### ADR22 — Preserve retrieval gains while testing the cost of more context

**Observed problem.** The title-zero hybrid improves average reference coverage
but drops passages the vector incumbent already retrieves. Iteration 023 varies
only the taught RRF constant, reconstructs its saved baseline exactly, and finds
that every cutoff-five variant still loses existing coverage. A better average
or an optional rubric point does not justify those losses under our frozen rule.

**Alternative and evidence.** Iteration 024 varies only final cutoff within each
fixed vector/RRF1 ranked list. Cutoff 10 is the smallest predeclared eligible size
for both methods. Iteration 025 then executes all 84 actual candidate queries and
matches every saved list and metric. Hybrid / 10 fully retrieves the references
for 25/35 answerable questions, against active vector / 5 at 18/35. Vector / 10
reaches 20/35. These are provisional retrieval labels, not correct-answer counts.
The exact [results, misses and resource scopes](../reports/goal-loop/retrieval-cutoff-capacity-024.md)
remain available to the reviewer.

**Trade-offs.** Hybrid / 10 improves multi-source coverage but loses LIM-07's
partial reference coverage compared with vector / 10. It uses two search branches.
Both candidates enlarge the input relative to vector / 5; serialized context
averages about 8,790 and 9,370 characters respectively. These are characters,
not model tokens. More passages may create source confusion or exceed the actual
serving window. Selecting cutoff 20 only for higher recall would ignore this cost.
Some required references are absent from both candidate lists and cannot be
recovered by changing final cutoff alone.

**Decision, verification and revisit.** Keep vector / 5 in the app. Test both
cutoff-ten policies with the same existing Phi3 model, prompt and output budget;
retain prior matching baseline receipts and review all new outputs. Only useful,
complete, supported answers without critical regression justify broader paired
development evaluation, context-capacity proof and eventual promotion. This work
strengthens R03's comparison rationale; it closes no R04, final, browser or Compose
gate. The taught basis is 2026 homework 4 Q6/Using this framework; cutoff values
and the no-loss rule are our adaptations, not lecturer guarantees.

### ADR23 — Reject larger context as an answer fix; investigate enforced output shape

The [eight-call follow-up](../reports/goal-loop/cutoff-answer-026/report.md) holds
model, prompt and output budget fixed while testing the two cutoff-ten policies.
Both produce four invalid outputs. Seven omit mandatory fields; one hybrid draft
contains both study aims but emits incorrect passage identifiers and edits the
quotations. All source windows, raw outputs, canonical errors and empty exports
were inspected and reviewed. No configuration is promoted and no favorable raw
fragment is substituted for a valid complete answer.

The observed allocated context is 4,096 tokens. Eight correlated server releases
report no truncation and all calls finish with a normal stop reason. This does
not establish capacity for arbitrary longer outputs, but it does not support
claiming observed truncation caused these particular failures. Do not increase
server settings or reduce required facts as an unexplained workaround.

The next proposed mechanism is schema-backed output, taught through Pydantic and
`responses.parse` in Module 4. Ollama documents JSON-schema output via its existing
OpenAI-compatible interface. Mapping that method to local Chat Completions is
our compatibility adaptation. A schema may prevent missing fields and also force
the model to generate additional unsupported text; semantic and whole-answer
review remain necessary. Start from the smaller incumbent context and hold the
prompt/model/output budget fixed to isolate the format mechanism. Preserve raw
outputs, schema identity, invalid attempts and exact quotation validation.

At checkpoint 026 this mechanism was not implemented or tested. A separate
predeclared experiment and affected software checks are required before using
it. The Q8 download and Compose installation approvals remain separate; neither
was granted or bypassed by this local eight-call test.

### ADR24 — Keep schema enforcement experimental after semantic regressions

**Requirement and choice.** Investigate the missing-field failures using the
2026 Module 4 structured-output principle and the already taught 2024 local
Chat Completions route. The `generation_json_schema` option maps the existing
answer contract to a fixed schema, only during generation. It defaults to false;
rewriting retains its different JSON object contract. Boolean conflicts and
non-local use of this option are rejected before inference. Request receipts
preserve the exact schema, messages, model identity, usage and failed output.

**Alternatives and trade-offs.** Retain generic JSON mode as the active baseline.
Use a fixed dictionary without dependency/lock changes for this compatibility
experiment; the exact lecturer example uses Pydantic and Responses.parse.
Dynamic ID/quote constraints, altered prompts, a larger output budget or different
model are separate choices, not bundled repairs. A fixed shape reduces omitted
fields but cannot prove semantic support or the status/claims relationship.

**Measured result.** [027](../reports/goal-loop/schema-answer-027/report.md)
reuses three incumbent contexts and two prompts; six new calls exactly reproduce
the old raw outputs. Those outputs already met the field shape. Therefore
[028](../reports/goal-loop/schema-cutoff-028/report.md) tests all eight saved
cutoff-ten cases that actually exposed missing fields. Required-field presence
improves from 1/8 to 8/8 and canonical validity from 0/8 to 6/8, but all six valid
outputs are refusals. Neither policy provides a complete supported answer or an
acceptable whole nonanswer. Some newly displayed prose is unsupported, a regression
from the baseline's blocked errors. Both candidates are rejected for promotion.

**Verification and revisit.** Fifteen targeted tests and all 121 full-suite tests
pass, including wrong sources, wrong quotations, status contradictions, schema
configuration conflicts, generation/rewrite isolation, no fallback and retained
token-limited output. Fourteen actual local calls, primary reviews, whole-answer
reviews and exported payloads are preserved. No source label or active setting
changed. Revisit only through a new predeclared generation/model hypothesis;
shape compliance is not evidence for full R04 credit or useful research. The
current baseline remains a quality-unselected candidate. Q8/download and clean
Compose execution still await their separately requested owner approvals.
