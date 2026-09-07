# Submission-candidate evidence and limitations

**Submission candidate, 7 September 2026.** The native app now binds the measured
Gemma/source-extract-complete/hybrid-top-10 configuration. The controlled pilot
result remains **8/12 with one critical relevance failure**; the internal quality
bar was not met. [D37](release-decisions.md#d37--submission-candidate-with-an-explicit-quality-exception)
records the owner's disclosed submission-policy exception. The final 18-question
inference test was not run. No course submission or official grade is claimed.

[The new native flow](../reports/final/native-bound-flow.json) proves the two
predeclared operational cases, six actual downloads, linked QA feedback, six
charts and restart persistence on the bound configuration. It is not a new
quality-selection sample. [The release gate](../reports/final/release-gate.json)
tracks publication checks. Anonymous exact-commit and clone evidence is produced
after packaging and retained outside that commit.

## Start with the actual evidence

- [Import manifest](../reports/release-migration/baseline-import.json): 425 explicitly
  selected files, with source hashes and exclusions. The original private Git
  history, secrets, personal research files and model weights were not imported.
- [Baseline check](../reports/release-migration/baseline-checks.json): 121 passed,
  zero skipped. [Latest complete software suite](../reports/checks.json):
  186 passed, zero skipped, on runtime `5a8dff9b921a68fb270e2428144f8c24ccdc45c6458fdb7e14c40d5577d653cc`.
  These include native ingestion/search and Streamlit
  AppTest plus synthetic provider contracts; software tests are not model quality.
- [Isolated-package rehearsal](../reports/submission-package-portability.json): the
  historical 172 checks pass without a private source sibling, using existing Python
  dependencies and a copied pinned MiniLM cache. The documented empty-cache
  failures preserve the required setup boundary; no new model download, fresh
  dependency installation or Compose execution is implied.
- Fresh dlt ingestion: three sources, 377 windows, 390 exclusions; corpus identity
  `a06955ab5c7a4f9c2d48213fae09980fe2628661f8ec5857527fe38d918dc7d0`.
  Source data, question splits, reference facts and original pass rules are frozen.
- [Real browser preview/download](../reports/release-browser/preview-download-check.json):
  ten CSV rows, 16,519 downloaded bytes, exact export round-trip. One stored preview
  and one answer-linked QA feedback record survived the native server restart.
  [The single-observation chart fix was visually verified](../reports/release-browser/preview-restart-chart-check.json).
  This establishes the preview/JSONL path, not LLM/PG/container execution.
- [Actual native LLM browser flow](../reports/release-browser/llm-flow.json): one
  separately planned QA attempt, a source-backed answer, actual JSON plus three
  CSV downloads, matching persisted answer/feedback and all six measured charts.
  The QA/LLM filter shows one request and one matching feedback; observed tokens
  are 2259 input and 18 output. This is candidate-native evidence, not selected
  release, independent researcher validation, PostgreSQL or Compose proof.
- [CPU Linux lock audit](../reports/release-migration/container-lock-audit.json):
  ARM64 and AMD64 each resolve 98 packages, with CPU PyTorch and no NVIDIA/triton
  packages. Non-Torch versions remain constrained to the existing lock. Resolution
  downloaded wheel archives, but installed no packages and did not build a container.
- [Actual Apple-silicon Compose rehearsal](../reports/container-rehearsal.json):
  official Docker installation verified, fresh pinned images/dependencies and
  encoder/model assets prepared, 172 software checks passed inside Linux ARM64,
  and all runtime services started healthy. Three browser calls yielded one valid
  abstention and two timeouts. Six downloads matched SQL/source bytes; answer-linked
  QA feedback and the six monitoring charts worked. Both pre-restart answer/feedback
  pairs survived with identical payload hashes. This closes infrastructure proof
  gaps without claiming a successful useful-answer or quality-selected release.

## Generation ledger and source-based reviews

The completed initial experiments contain **78 actual local generation attempts**:
2 feasibility + 48 model/prompt pilot + 4 format diagnostic + 24 precision repair.
They are distinct from imported historical calls. No retries, paid calls, model
judge or final-set inference occurred in those runs. The following adaptive
[source-span feasibility](../reports/release-quality/source-spans-feasibility-index.json)
added five calls and the [concise diagnostic](../reports/release-quality/source-spans-concise-diagnostic-index.json)
added five more: **88 completed local attempts before the source-excerpt experiment**.
The [source-excerpt feasibility](../reports/release-quality/source-extract-feasibility-index.json)
added ten calls, and the separate native browser QA added one. Thus **99 completed
attempts preceded the six-slice source-excerpt pilot**. Its 24 completed calls
bring that subtotal to **123**, reconciled against actual provider journals.
Checked and reasoned Gemma feasibility added five calls each, the Phi3 source-
selection comparison added ten, and known-reference diagnosis added two. The
development/native ledger totals **145 completed actual local generation attempts**. The two
oracle-context calls are not normal quality samples or selection evidence. The historical
[attempt reconciliation](../reports/release-quality/attempt-accounting.json) links
actual provider journals to results and retains pending/orphan gaps. Planned calls
are not silently treated as executed. All source-based judgments are provisional reviews
by the implementing assistant, with candidate identity known, not independent
human or biomedical validation.

The later [container browser rehearsal](../reports/container-runtime/browser-flow.json)
adds **three operational QA attempts**, including two timeout failures. There are
therefore 148 observed attempts across those historical records. The new
[final native flow](../reports/final/native-bound-flow.json) adds two separate
operational attempts, making 150 observed generation attempts across all three
ledgers. The [separate rewrite diagnostic](../reports/final/rewrite-diagnostic.json)
adds twelve rewrite calls and 24 searches, with zero additional generation calls.
Rewrite attempts are not answer-generation samples. The
container cases are not additional development-selection samples, a final test,
or evidence for pooling a single model-accuracy percentage.

| Experiment and context | Arm | Fully acceptable | Output errors | Critical answers |
|---|---|---:|---:|---:|
| Initial pilot; vector/5 | Phi3 / evidence_first | 0/12 | 6 | 2 |
| Initial pilot; vector/5 | Phi3 / numbered_evidence | 2/12 | 9 | 0 |
| Initial pilot; vector/5 | Gemma3 / evidence_first | 3/12 | 1 | 2 |
| Initial pilot; vector/5 | Gemma3 / numbered_evidence | 4/12 | 1 | 2 |
| Format diagnostic; hybrid/10/title0 | Gemma3 / object mode | 1/2 | 1 | 0 |
| Format diagnostic; hybrid/10/title0 | Gemma3 / schema mode | 1/2 | 1 | 0 |
| Precision repair; hybrid/10/title0 | Gemma3 / numbered_evidence | 4/12 | 4 | 1 |
| Precision repair; hybrid/10/title0 | Gemma3 / numbered_precise | 4/12 | 4 | 0 |
| Source-span feasibility, five cases | Gemma3 / source_spans_complete | 3/5 | 0 | 1 |
| Source-span concise diagnostic, same cases | Gemma3 / source_spans_concise | 2/5 | 2 | 0 |
| Source-excerpt feasibility, same cases | Gemma3 / source_extract_concise | 3/5 | 0 | 0 |
| Source-excerpt feasibility, same cases | Gemma3 / source_extract_complete | 4/5 | 0 | 0 |
| Source-excerpt six-slice pilot | Gemma3 / source_extract_concise | 6/12 | 0 | 1 |
| Source-excerpt six-slice pilot | Gemma3 / source_extract_complete | 8/12 | 0 | 1 |
| Checked selection feasibility, five cases | Gemma3 / source_extract_checked | 3/5 | 0 | 1 |
| Reasoned selection feasibility, same cases | Gemma3 / source_extract_reasoned | 3/5 | 0 | 1 |
| Phi3 source-selection feasibility, same cases | Phi3 / source_extract_checked | 1/5 | 3 | 1 |
| Phi3 source-selection feasibility, same cases | Phi3 / source_extract_reasoned | 2/5 | 0 | 2 |

Raw outputs, immutable call receipts, judgments, canonical/whole-answer reviews
and per-question summaries are linked from the [initial pilot index](../reports/release-quality/pilot-index.json),
[format index](../reports/release-quality/format-diagnostic-index.json) and
[repair index](../reports/release-quality/precision-repair-index.json).
Their execution status stays separate from review completion. Dispositions:
[pilot rejected](../reports/release-quality/pilot-disposition.json),
[format diagnostic](../reports/release-quality/format-diagnostic-disposition.json),
[precision repair rejected for release](../reports/release-quality/precision-repair-disposition.json).

The precise instructions removed an observed critical semantic failure, but both
repair arms still delivered only four complete answers. Source copying and missing
fields blocked intended answers. No full validated cross-publication comparison
was delivered in either arm. Zero critical failures alone is not useful-answer
certification. The [next transport adaptation](release-decisions.md#d33--source-span-transport-after-observed-copy-failures)
selects exact source positions without fuzzy quotation repair; its actual quality
must pass the same unchanged completeness and semantic review.

The later [source-excerpt feasibility review](../reports/release-quality/source-extract-feasibility-disposition.json)
does establish complete supported cross-publication comparisons in both arms.
The complete prompt additionally supplies electronic medical records in PAR-01.
Both still miss LIM-02's available design qualification. These are five preselected
development cases, not a general 80% accuracy estimate. The
[six-slice pilot](../reports/release-quality/source-extract-pilot-plan.json) broadened
the comparison to 12 cases per arm without changing sources, facts or pass rules.
Its [completed disposition](../reports/release-quality/source-extract-pilot-disposition.json)
rejects both: each substitutes unrelated ventilation material for a genetic
association caveat. The detailed prompt gains the records question and an accession
refusal, but zero quote-format errors do not cancel that critical relevance error.

The subsequent [checked selection](../reports/release-quality/source-extract-checked-feasibility-disposition.json),
[reasoned selection](../reports/release-quality/source-extract-reasoned-feasibility-disposition.json)
and [Phi3 recheck](../reports/release-quality/phi3-source-selection-feasibility-disposition.json)
also fail the promotion gate. A model explanation can rationalize the wrong source
relationship; it is not an independent judge. These are bounded feasibility cases,
not interchangeable denominators or a single pooled model-accuracy estimate.

A review wording error about the number of nonliteral EXA-01 quotes was corrected
with [preserved review versions](../reports/experiments/answers-1927f1d9-ad6b-4bf2-8044-d2d97f42dd4c/review-revision-log.json).
The current diagnosis says one nonliteral quote; judgments and totals did not
change. The historical precise arm's missing transport receipts are also disclosed;
it cannot be reused as complete current-runtime selection evidence.

## Retrieval comparison and failure diagnosis

All retrieval evaluation uses the same 42 development questions. The denominator
below is 35 answerable questions; seven corpus-absence questions remain in the run
but are not Hit/MRR opportunities. Reference labels are provisional and non-exhaustive.

| Actual configuration | Full annotated reference coverage | Mean reference coverage | Hit at k | MRR at k |
|---|---:|---:|---:|---:|
| Vector / 5 | 18/35 | 0.5667 | 0.6000 | 0.4695 |
| Vector / 10 | 20/35 | 0.6667 | 0.7429 | 0.4906 |
| Hybrid / 5 / title2 / RRF50 | 15/35 | 0.4952 | 0.5714 | 0.3452 |
| Hybrid / 10 / title2 / RRF50 | 21/35 | 0.6429 | 0.6857 | 0.3617 |

The [factorial](../reports/release-quality/retrieval-factorial.json) contains 168
actual searches. Subsequent title-weight ablation and fixed-candidate rank replays
are identified separately; rank replays are not new search calls. The
[fresh hybrid/10/title0/RRF50 verification](../reports/release-quality/hybrid-zero-fresh.json)
contains 42 actual searches and fully covers annotated references in **26/35**
questions, with mean reference coverage **0.7762**. It supplies identical saved
contexts to the later generation arms. More reference coverage does not establish
answer correctness or justify promoting a default by itself.

The apparent PAR-01 loss under frozen IDs has an annotation explanation: the
retrieved Italian abstract states retrospective analysis and a retrieved methods
passage states electronic medical records. Those facts are available even though
one equivalent abstract passage was not listed as a reference. The bank stays
unchanged; this interpretation is disclosed separately from mechanical counts.
Other misses remain genuine: COM-02 lacks the review's PARM-90% window; PAR-02 omits
the guideline methods paragraph; LIM-01's relationship caveat is outside both
candidate pools. Do not infer a missing percentage, conflate study types, or treat
a missing passage/table as absence from all CCHS literature.

The [252-search representation ablation](../reports/release-quality/representation-results.json)
compares three embedding text templates and vector/hybrid at fixed top-10. Content
alone improves some missing references but loses exact-identifier and comparison
evidence. The title/content hybrid retains the highest complete reference count,
26/35; none of the six variants retrieves LIM-01's required caveat. All three
templates have zero encoder-truncated inputs on these windows. The separate
[full-rank diagnostic](../reports/release-quality/full-rank-miss-diagnostic.json)
locates LIM-01's reference at lexical position 46 and vector position 101 (zero
based), explaining why a small candidate-pool increase cannot establish coverage.
These are dataset-specific observations, not a universal ranking rule.

The [two known-reference diagnostics](../reports/release-quality/reference-oracle-review.json)
separate two failure modes. With the original reference paragraph supplied,
LIM-01 returns the correct inconsistency statement but still omits the required
exceptions. LIM-02 supplies both actual design and heterogeneity under a single
reference paragraph, whereas it had refused under ten retrieved passages that
already included that paragraph. Retrieval coverage and generation distraction/
completeness both need attention; success on an oracle context is not a runtime gain.

## Rubric-to-evidence route

The [official rubric](https://github.com/DataTalksClub/llm-zoomcamp/blob/main/project.md#evaluation-criteria)
controls the award. Maxima are available points, not awarded or banked points.

| Criterion | Maximum | Implementation, result and reproduction evidence | Limit |
|---|---:|---|---|
| Problem | 2 | [Use cases](../README.md#the-problem-and-useful-output), [source manifest](../data/manifest.json) | Researcher benefit is intended, not measured |
| Retrieval with LLM | 2 | [RAG](../navigator/rag.py), [native flow](../reports/final/native-bound-flow.json), [setup](setup.md) | Two operational cases do not establish general quality |
| Retrieval evaluation | 2 | [Factorial](../reports/release-quality/retrieval-factorial.json), [active choice](../reports/final/selection-2026-09-07.json) | Provisional, incomplete reference labels; losses retained |
| Answer evaluation | 2 | [Paired source-extract review](../reports/final/selection-2026-09-07.json), [active config](../configs/app.json) | 8/12 and one critical failure; internal bar not met |
| Interface | 2 | [Streamlit](../app.py), [actual downloads](../reports/final/native-bound-flow.json), [walkthrough](setup.md) | Native route demonstrated |
| Ingestion | 2 | [dlt pipeline](../navigator/corpus.py), [fresh counts](../reports/final/native-setup.json), [ingest command](setup.md) | Tables/figures excluded |
| Feedback and monitoring | 2 | [Storage](../navigator/storage.py), [six charts](../README.md#interface-exports-and-monitoring), [flow](../reports/final/native-bound-flow.json) | QA feedback is not researcher satisfaction |
| Containers | 2 | [Compose](../compose.yaml), [historical execution](../reports/container-rehearsal.json), [setup](setup.md#full-compose-route--execution-pending) | Historical Phi3; bound Gemma execution unproved |
| Reproducibility | 2 | [Setup/restart](setup.md), [locks](../uv.lock), [source data](../data/README.md), [release gate](../reports/final/release-gate.json) | Existing-assets native proof; public-clone receipt follows commit |
| Hybrid retrieval | 1 | [Both branches and fusion](../navigator/retrieval.py), [ablation](../reports/release-quality/retrieval-factorial.json) | Improvement is task-specific |
| Reranking | 1 | [Zero-based RRF](../navigator/retrieval.py), [rank diagnosis](../reports/release-quality/full-rank-miss-diagnostic.json), [course mapping](course-sources.md) | Possible overlap with hybrid credit |
| Query rewriting | 1 | [Bounded implementation](../navigator/rewriting.py), [diagnostic status](../README.md#best-practices-and-decisions) | Disabled; no automatic bonus claim |
| Cloud | 2 | [Deployment scope](../reports/final/compose-final.json) | No cloud deployment; no points claimed |
| Discretionary additions | Up to 3 | [Traceable research exports](../navigator/exports.py), [browser evidence](../reports/final/native-bound-flow.json) | Examiner judgment; no guaranteed award |

## Release blockers and completion rule

Sixteen historical reports had local path metadata redacted in the new copy with
[before/after hashes](../reports/release-migration/public-path-redactions.json).
Metrics and raw model answers were not rewritten. Original private files remain
unchanged. The preliminary package credential scan is scoped evidence, not a
blanket guarantee; rerun publication checks on the final concrete package.

The owner authorized the [concrete Compose scope](container-installation-scope.md).
Docker Desktop 4.90.0 is installed with verified official checksum, Docker signing
identity and Apple notarization. The empty engine was verified at six CPUs,
10 GiB configured RAM and a fresh 20 GiB disk. The
[Compose execution report](../reports/container-rehearsal.json) records the
completed operations and a corrected initial default-resource deviation. Installation, CPU
lock resolution and native tests do not replace a complete container rehearsal.
The first real ARM64 build passed with hash-checked dependencies:
[complete build log](../reports/container-runtime/compose-build.log) and
[built image identities](../reports/container-runtime/built-images.json).
Fresh ingestion and pinned encoder preparation passed, followed by
[172 software checks with zero skips inside Linux ARM64](../reports/container-runtime/software-checks.json).
The [image integrity check](../reports/container-runtime/container-image-integrity.json)
verified the existing code/configuration identities, non-root Python image and
exclusion of the private environment and Git history.
The [operational browser cases](../reports/container-runtime/browser-rehearsal-plan.json)
were recorded before generation; these are QA cases, not the final evaluation.
All three ran once. The two answerable requests timed out at the configured
120 seconds, before and after restart; the no-evidence request returned a valid
abstention in about 42 seconds. [All six downloaded exports](../reports/container-runtime/browser-downloads.json)
matched the stored answer payloads and frozen passage spans. Two pre-restart
answer/feedback pairs were retained unchanged, and a third pair was added after
restart. The final QA dashboard included failures and all three linked ratings.
No validated claims were produced, so claim/tag exports remain unproved for this
container candidate. The existing quality gate remains unchanged.

After the three calls, the server's optional cloud features were disabled with
`OLLAMA_NO_CLOUD=1`. [Runtime checks](../reports/container-runtime/local-only-checks.json)
confirmed the flag, the disabled-cloud log and healthy services. Model identity
and all database payloads were retained; no new inference ran after this setting
change. The complete useful-answer rehearsal still needs a suitable candidate.
Observed [resource samples](../reports/container-runtime/resource-summary.json)
stayed within the owner's bounds. [The setup guide](setup.md#observed-container-results-and-next-decision)
distinguishes the actual context, timeout diagnostics, asset bytes and remaining
experiment from successful quality evidence.
The optional twelve-query rewrite diagnostic ran after binding, demo and
documentation were ready, before the 23:20 Jerusalem start cutoff. All twelve
outputs exactly repeated their original questions; ranks were identical and no
benefit was observed. It added 6.3 seconds mean per query in this run. Rewriting
remains disabled. This diagnostic ran no answer generation and does not change
the pilot's historical score. [Raw evidence](../reports/final/rewrite-diagnostic.json)
and [intent review](../reports/final/rewrite-diagnostic-review.json) retain all calls.
The owner authorized commit/publication/tag after mandatory checks; the owner alone
saves the course form. Exact public-commit verification follows packaging.

[Source-preservation recheck](../reports/release-migration/original-source-recheck.json)
confirms all 425 imported files remain unchanged in the private predecessor.
[Protected inputs](../reports/release-migration/protected-input-recheck.json)
confirm the new raw sources, manifest and question banks remain frozen. The
representation report's six local-cache path fields were redacted separately with
[before/after hashes](../reports/release-migration/representation-metadata-redaction.json);
that redaction changes no ranking, context or metric.

The original internal contract remains unmet: do not mark LOCAL_CORE_EVIDENCE_READY until the strict quality contract, full
paired development evidence, active selected runtime, full browser flow, clean
Compose and once-only final assessment are all demonstrated. The 18 final queries
have not been run during this release work. Source labels remain provisional;
research findings and tags remain pending human review. Official score and
submission eligibility are unverified. Three peer reviews are separate course work.
