> **Public-release amendment (2026-09-07):** Work now targets the separate
> `cchs-evidence-navigator-zoomcamp` repository. The owner approved installed
> Gemma 3 12B as an explicitly non-taught model exception; all original quality
> gates remain. Earlier private-only/model-exclusion and execution-status statements
> are historical. Use [current release evidence](release-status.md),
> [release decisions](release-decisions.md) and [setup](setup.md) for this version.

# Course source map and attribution

## Current public-copy adaptations

The earlier experiment notes below are dated history, including rejected routes.
The current [release ledger](release-status.md) and [decisions](release-decisions.md)
govern execution status. No generated quality score is an instructor-awarded score.

- Module 1 context construction and Module 4 exact source-record lookup support
  the request-local passage and source-span adapters. Display spans preserve every
  source character; their numbering, position receipts and strict field ownership
  are original application code. Neither numbering nor a genuine quotation proves
  that the selected source supports the generated claim.
- The Module 4 schema examples cited below motivate the local schema-compatible
  output request. It is now exercised in explicit format/source-pointer experiments,
  rather than claimed universally disabled. Old no-schema statements describe
  their particular historical runs. The existing OpenAI client is retained.
- Module 4 paired comparisons support frozen contexts, failed-attempt accounting
  and per-question source reviews. Additional partial-coverage counts are diagnostic
  project adaptations; they do not replace the original completion criteria.
- The short selection explanation in an experimental source-excerpt prompt is
  original structured-output glue. It stays in raw diagnostic output and is never
  an independent judge or scientific evidence. Its measured failures are retained.
- Module 5 charting supports the generation-duration bar chart, verified with an
  actual single-observation browser screenshot. Native JSONL restart evidence does
  not establish PostgreSQL/container persistence.
- The CPU-specific Docker locks package the same taught vector stack with existing
  resolved package versions and official CPU Torch artifacts. Resolving a lock is
  a compatibility preparation step, not an executed clean container installation.

Gemma 3 12B remains the explicitly owner-approved **non-taught model exception**.
Source-span glue adds no new application library, embedding model, biomedical
analysis framework or approximate citation matcher.

Official course: https://datatalks.club/docs/courses/llm-zoomcamp/

Teaching repository: https://github.com/DataTalksClub/llm-zoomcamp

Rubric: https://github.com/DataTalksClub/llm-zoomcamp/blob/main/project.md

Cohort: https://courses.datatalks.club/llm-zoomcamp-2026/

The local English handbook and selected project brief are input guidance. Their
names and historical hashes are recorded in `reports/source-inputs.json`; the public
application does not depend on owner-local handbook paths.
The research review has not read every companion transcript/addition completely;
this source map supports the specific methods implemented here.

The clean local teaching copy is pinned to
`bc7b6aad6b92a5611d3d37bf7521a363f3b9d398`. Consult current cohort logistics
separately. Raw-web and rendered GitHub views can expose different historical
submission links; the cohort platform is the logistics reference.

| Implementation | Taught source | Adaptation in this project |
|---|---|---|
| Context/prompt/Responses and component separation | [Module 1 RAGBase](https://github.com/DataTalksClub/llm-zoomcamp/blob/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/01-agentic-rag/code/rag_helper.py) | Corpus fields, research instructions, exact quote/ID validation and fail-closed UI |
| Lexical retrieval | [Module 1](https://github.com/DataTalksClub/llm-zoomcamp/tree/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/01-agentic-rag) | title/section/content boosts and publication/type filters |
| MiniLM, normalization and vector retrieval | [Module 2](https://github.com/DataTalksClub/llm-zoomcamp/tree/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/02-vector-search) | Original article windows, row mapping, revision/truncation report |
| Overlap and RRF rank fusion | [2026 homework 1/2/4](https://github.com/DataTalksClub/llm-zoomcamp/tree/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/cohorts/2026) | Stable BioC coordinates and new corpus; no homework data copied |
| dlt load to DuckDB | [dlt filesystem pipeline](https://github.com/DataTalksClub/llm-zoomcamp/blob/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/cohorts/2026/workshops/dlt/code/filesystem_pipeline.py) | Licensed literature records instead of personal agent logs; explicit index export |
| Evaluation design and metrics | [Module 4](https://github.com/DataTalksClub/llm-zoomcamp/tree/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/04-evaluation) | Provisional passage labels, source-support checks and frozen context comparisons |
| Streamlit, PostgreSQL/psycopg, feedback and charts | [Module 5 code](https://github.com/DataTalksClub/llm-zoomcamp/tree/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/05-monitoring/code) | Request UUIDs, idempotent feedback, JSONB payloads, non-destructive initialization, five charts |
| Containerization | [Module 5](https://github.com/DataTalksClub/llm-zoomcamp/tree/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/05-monitoring) | App/database/ingestion services and project-specific volumes/health checks |

The modular RAG flow and SQL persistence pattern are adapted from DataTalksClub
teaching examples. Original project glue includes BioC parsing, evidence contracts,
validation, local development JSONL, corpus/source checks, CSV formula escaping,
test fixtures and operational errors. Python standard-library testing, Git and
dependency locks are development practices, not claimed new course algorithms.

No student project is copied. No clinical NLP framework, graph database, untaught
OCR stack or optional historical wrapper is introduced. Optional Modules 6/7
remain guidance for subsequent compatible, separately evaluated improvements.

Current project dependencies are resolved in `uv.lock`; declared lower bounds and
resolved versions are different facts. Transitive dependencies do not expand the
allowed application methods. Generic embeddings have no assumed biomedical or
Hebrew quality advantage.

## Remediation attribution

The 2026 Homework 4 grid (`cohorts/2026/04-evaluation/homework.md`, Q6) supports
the measured RRF-parameter comparison in `tools/compare_retrieval_grid.py`. Module 1
Responses/context and Module 4 paired-prompt evaluation support the fixed flow and
checkpointed answer comparisons. Module 5 pandas/Streamlit supports the new count
chart and origin-filtered dashboard. Strict field ownership, content hashes for
reviews, CSV provenance columns and QA-origin isolation are explicit project
adaptations of those patterns, not claims that the instructor supplied this code.

The optional Module 6 reranking lesson demonstrates RRF; it does not establish
independent credit for counting the existing fusion twice. Module 1 function calling
demonstrates reformulated search queries, but this release has no measured rewriting
route. No student-only cross-encoder or unrelated local model is introduced.


## Local remediation provenance

| Use | Taught evidence | Original adaptation / limitation |
|---|---|---|
| Local Phi3 through OpenAI Chat Completions | [2024 qa_faq.py](https://github.com/DataTalksClub/llm-zoomcamp/blob/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/cohorts/2024/02-open-source/qa_faq.py) | Strict JSON, quote validation, endpoint restriction and call receipts are project adapters |
| Gemma 2B alternative | [2024 open-source homework](https://github.com/DataTalksClub/llm-zoomcamp/blob/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/cohorts/2024/02-open-source/homework.md) | Compare on the new corpus; exercise settings are not guaranteed optimal |
| Ollama container and weight persistence | [2024 Compose example](https://github.com/DataTalksClub/llm-zoomcamp/blob/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/cohorts/2024/02-open-source/docker-compose.yaml) | Merge into current application Compose; current image manifests verified separately |
| RRF as reranking | [Optional Module 6 lesson](https://github.com/DataTalksClub/llm-zoomcamp/blob/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/06-best-practices/lessons/03-reranking.md) | Zero-based homework convention retained; no assumed double scoring |
| Reformulated search query | [Module 1 function calling: Sending the question with the tool](https://github.com/DataTalksClub/llm-zoomcamp/blob/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/01-agentic-rag/lessons/13-function-calling.md#sending-the-question-with-the-tool), [agent loop](https://github.com/DataTalksClub/llm-zoomcamp/blob/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/01-agentic-rag/lessons/14-agentic-loop.md#encouraging-multiple-searches) | Course demonstrates query reformulation through a model-selected search argument. Our adaptation is one explicit local JSON reformulation, with identifier checks and fallback; it does not implement the course's multi-call loop or establish Phi3 tool-calling support. |

The launch flag `--server.fileWatcherType none` is our compatibility adjustment,
verified against the installed Streamlit configuration option. It disables hot
reload because the development watcher inspected optional Transformers image
modules and logged missing-image-dependency errors. It introduces no library or
course algorithm; the operational trade-off is restarting after code edits.
| Completeness-aware review and research tables | Modules 4/5 evaluation, source metadata and tabular outputs | Required facts, qualification labels and literal-term proposal rules are our task-specific applications, not taught biomedical methods |

Current [Ollama compatibility](https://docs.ollama.com/api/openai-compatibility)
and [Docker documentation](https://docs.ollama.com/docker) were used only to verify
compatibility of the taught route. Their other model suggestions do not expand the
approved toolbox. Source code was read; course scripts were not executed.

## Decision-refinement adapters

- Module 1 minsearch field selection and Module 2 document-to-vector encoding
  support the heading ablation. `section_heading` is our source metadata; testing
  it in the text/template is an adaptation, not an instructor claim that it helps.
- Explicit encoder-cache initialization and offline serving package the same
  taught SentenceTransformers route. They add no model or retrieval algorithm.
- Module 5 answer/feedback persistence and pandas aggregation underpin origin
  validation in both adapters and the all-scope dashboard. The policy and regression
  tests are our engineering work; historical live PostgreSQL persistence is documented in the [container rehearsal](../reports/container-rehearsal.json).
- RRF precision: the pinned optional **lesson markdown** manually passes the
  zero-based `enumerate` rank to `compute_rrf`; the optional notebook
  `hybrid-search-and-reranking-es.ipynb`, physical cell 39, passes `rank + 1`.
  Homework 2/4 also use zero-based ranks. Do not describe all Module 6 code as
  one-based. This project retains the zero-based convention and k=50.

## Claude-note compatibility and evaluation corrections

JSON object mode is a **project API adapter**, not a claim that the 2024 example
used this argument. The taught [2024 OpenAI-client/Ollama call](https://github.com/DataTalksClub/llm-zoomcamp/blob/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/cohorts/2024/02-open-source/qa_faq.py)
is retained. Current [Ollama compatibility documentation](https://docs.ollama.com/api/openai-compatibility)
supports `response_format`; we request a JSON object and still enforce the same
schema, source IDs and exact quotations. No schema-constrained decoding or measured
quality improvement is claimed. No model/framework was added.

The read-only preflight uses [POST /api/show](https://docs.ollama.com/api-reference/show-model-details)
for architecture/quantization and [GET /api/ps](https://docs.ollama.com/api/ps) for
currently allocated context. These are operational diagnostics, not generation.
The architecture limit does not prove the loaded context; a character/token ratio
or near-window token count is not a verified truncation detector. No server
window was changed. The timeout override is bounded application configuration
and participates in the experiment fingerprint.

Module 4's paired evaluation motivates preserving failed outputs in the comparison.
Continuing after a completed schema-invalid output, while stopping on a service
failure, is our experiment-accounting policy. It adds no evaluation model and does
not weaken answer validation. One model with two prompts and explicit assistant
review is the default route; automated judging remains optional.

## Active Goal experiments — complete source-based review

- [Module 1 context construction](https://github.com/DataTalksClub/llm-zoomcamp/blob/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/01-agentic-rag/code/rag_helper.py)
  and [Module 4 source-ID lookup](https://github.com/DataTalksClub/llm-zoomcamp/blob/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/04-evaluation/lessons/12-rag-answers.md)
  support the separation of retrieved source identity from model formatting.
  `short_ids` is our deterministic request-local transport adapter, not code copied
  from the course. Its unsuccessful pilot does not justify enabling it by default.
- The [2024 local FAQ example](https://github.com/DataTalksClub/llm-zoomcamp/blob/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/cohorts/2024/02-open-source/qa_faq.py)
  makes ordinary Chat Completions calls without `response_format`. Iteration 010
  compares that format setting while preserving our strict output contract and
  the two existing prompts. No new provider, library or course accuracy claim is
  introduced. Six observed outputs remain semantically unchanged and unsuccessful.

- Module 4 paired evaluation supports comparing fixed contexts and preserving
  every failed result. `navigator/whole_review.py` is our explicit whole-prose
  and export-review enforcement; agent judgments remain provisional.
- The [2024 local-model example](https://github.com/DataTalksClub/llm-zoomcamp/blob/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/cohorts/2024/02-open-source/qa_faq.py)
  combines instructions, labeled QUESTION and CONTEXT in one user message.
  The `course_user` candidate adopts that composition while preserving this
  project's existing evidence JSON and strict answer schema. Both variants use
  identical `evidence_first` instructions. This is a layout experiment, not an
  assertion that the course demonstrated our source validator or biomedical task.
- The first complete Phi3 comparison rejected `coverage_first`: no acceptable
  response in either seven-question arm. Gemma 2B was also rejected after the
  same-context 14-call comparison; mechanical citations did not prevent wrong
  study attribution and unsupported conclusions. Original results and reviews
  remain under [iteration records](../reports/goal-loop/iterations/).

No failed candidate changed the active configuration. Source/course files were
read statically; no source script was run and no model or dependency was installed.


## Formatting and source-attachment diagnostics (012–019)

- [2024 ordinary-prose local RAG](https://github.com/DataTalksClub/llm-zoomcamp/blob/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/cohorts/2024/02-open-source/qa_faq.py)
  and [Module 1 context projection](https://github.com/DataTalksClub/llm-zoomcamp/blob/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/01-agentic-rag/code/rag_helper.py)
  inform the ordinary-prose and compact-context diagnostics. Removing output
  contracts temporarily diagnoses formatting burden; those outputs are never
  presented as accepted application answers.
- [Module 1 loop history](https://github.com/DataTalksClub/llm-zoomcamp/blob/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/01-agentic-rag/lessons/14-agentic-loop.md)
  and [Module 3 staged research synthesis](https://github.com/DataTalksClub/llm-zoomcamp/blob/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/03-orchestration/flows/6_multi_agent_research.yaml)
  support carrying prior outputs into later tasks. Our bounded two-call formatting
  prototype is an adaptation, not execution of that Kestra flow. The example's
  instruction to infer missing facts is explicitly unsuitable for this project
  and was rejected. No Kestra, Gemini or Tavily service was added or run.
- [Module 4 source-answer lookup](https://github.com/DataTalksClub/llm-zoomcamp/blob/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/04-evaluation/lessons/12-rag-answers.md)
  uses an exact document ID to recover the source record. The claim/E-label to
  immutable full-window attachment is our adapter of that lookup principle, not
  a taught biomedical validation technique or proof of entailment. It is confined
  to diagnostic prototypes; the canonical application remains unchanged.
- The all-abstention nomination repair is original evaluation software enforcing
  the owner's frozen contract. Its synthetic tests and old/new recomputation are
  consistency evidence, not instructor-awarded points or new model experiments.


## Claims/source isolation and precision preparation (020–022)

The claims-only and per-window prototypes are original adapters around the taught
2024/Module 1 source-context RAG call and Module 4 exact source-record lookup.
They add no agent framework or scientific method. Both were rejected after real
local calls; smaller output and correct source attachment do not establish useful
or entailed answers. All final scientific facts/qualifications remain required.

The 2024 `huggingface-mistral-7b.ipynb` physical cell 10 demonstrates quantized
loading (`load_in_4bit=True`), while `qa_faq.py` demonstrates the Phi3/Ollama
Chat Completions route. The exact proposed Phi3 Mini Q8 tag applies that precision
trade-off to the existing model family. It is our adaptation, not a lecturer's
exact Q8 recommendation. Its [registry metadata and alternatives](../reports/goal-loop/model-feasibility.md)
are verified separately; no model weights or dependencies were downloaded. The
exact provider tag is prepared, with local-only/digest/no-fallback checks retained;
authorized setup and a successful experiment remain necessary before any use as
the selected application model.

## Retrieval-coverage continuation (023–025)

[2026 homework 4, Q6 and Using this framework](https://github.com/DataTalksClub/llm-zoomcamp/blob/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/cohorts/2026/04-evaluation/homework.md#q6-tuning-hybrid-search)
teaches the RRF grid 1/50/100/200 and evaluation of returned-result count with
fixed ground truth. Iteration 023 uses that grid without changing zero-based
fusion. Cutoffs 5/10/20, the reference-coverage nomination rule and the decision
to inspect actual context burden are project adaptations. The actual MiniLM /
minsearch implementation verifies the replay in iteration 025. These checks add
no new framework, change no scientific labels and do not prove model quality or
eligibility for duplicate RRF credit.

## Schema-backed output: implemented experiments 027–028

[Module 4 ground-truth generation](https://github.com/DataTalksClub/llm-zoomcamp/blob/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/04-evaluation/lessons/02-ground-truth.md)
defines `Questions` with Pydantic and passes it as `text_format` to
`responses.parse`; [evaluation_utils.py](https://github.com/DataTalksClub/llm-zoomcamp/blob/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/04-evaluation/code/evaluation_utils.py)
contains `llm_structured`. These are implemented teaching examples, read
statically. No course model call or retry helper was executed.

The implemented local adaptation expresses the unchanged answer structure in
the existing Ollama Chat Completions request. [Ollama's structured-output documentation](https://docs.ollama.com/capabilities/structured-outputs)
verifies the compatibility mechanism, not course provenance or local success.
The [027–028 experiments](../reports/goal-loop/schema-cutoff-028/report.md)
execute that mapping. A fixed dictionary avoids a new direct dependency; the
lecturer used Pydantic with Responses.parse, not this exact local request. The
option is false by default and applies only to generation, not rewriting. It adds no taught
status to the unrelated example models in the provider documentation. A valid
shape cannot establish truth, exact citation, completeness or an acceptable
abstention; the original validators/reviews remain mandatory.
