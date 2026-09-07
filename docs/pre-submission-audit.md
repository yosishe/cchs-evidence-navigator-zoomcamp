# Pre-submission audit — executed scope and remaining gates

Updated **7 September 2026** for the submission candidate. The owner accepted the
failed internal quality bar with prominent disclosure, conditional on all final
operational/package gates. [Current release gate](../reports/final/release-gate.json)
and [D37](release-decisions.md#d37--submission-candidate-with-an-explicit-quality-exception)
define this narrower publication decision. The course form remains owner-only.

The 50 checks below are the project handbook's acceptance checklist, not 50
mandatory course rules. Course requirements, scored features, optional routes and
stricter owner quality conditions are distinguished in [readiness](readiness.md).
PASS_WITH_SCOPE covers only the stated observation; PARTIAL and BLOCKED remain
open. NOT_APPLICABLE earns no credit; CONDITIONAL applies only to that chosen route.
Scientific validation and guaranteed full marks are not claimed.

The old [5 September audit snapshot](../reports/pre-submission-audit.json) remains
historical evidence. This table and the [final machine-readable audit](../reports/final/release-gate.json)
supersede its current-state observations without rewriting original run results.

| Check | Status | Evidence | Observation / remaining work |
|---|---|---|---|
| <a id="pt01"></a>PT01 — Bind the audit to the correct course and rules | PASS_WITH_SCOPE | [Evidence](readiness.md) | Live rubric, attempt-3 form, UTC calendar, dashboard passing setting and deployed platform validation source checked on 7 September. Personal eligibility remains unverified. |
| <a id="pt02"></a>PT02 — Prove the corpus is original and usable | PARTIAL | [Evidence](../reports/corpus-preparation.json) | Licensed original literature snapshots and exclusions present; complete scientific/correction review pending. |
| <a id="pt03"></a>PT03 — Check authorship and explainability | PARTIAL | [Evidence](../reports/../docs/course-sources.md) | Course-code adaptations attributed; owner explanation has not been tested. |
| <a id="pt04"></a>PT04 — Enforce the course-only implementation boundary | PASS_WITH_SCOPE | [Evidence](course-sources.md) | Methods are course-mapped; Gemma 3 12B is the explicitly owner-approved non-taught model exception. Adaptation glue is identified; no new RAG framework. |
| <a id="pt05"></a>PT05 — Make the problem understandable to a stranger | PARTIAL | [Evidence](../reports/answer-baseline/README.md) | README problem and diagnostic live answers reviewed by an assistant; unfamiliar human reader and researcher utility remain untested. |
| <a id="pt06"></a>PT06 — Verify the public repository at the exact commit | OWNER_HANDOFF | [Evidence](readiness.md#exact-public-target-test-after-publication) | Anonymous exact-commit verification follows packaging; receipt is outside the commit. |
| <a id="pt07"></a>PT07 — Reproduce from a fresh environment | PARTIAL | [Evidence](../reports/submission-package-portability.json) | Historical isolated-copy 172 and Linux 172 checks passed. New native route reused assets; public-clone ingestion is checked after publication, not a fresh installation. |
| <a id="pt08"></a>PT08 — Validate actual dependency versions | PASS_WITH_SCOPE | [Evidence](../reports/final/native-preflight.json) | Bound model digest, Python 3.12.14 and actual 4,096-token context observed; dependency locks retained. Native evidence does not prove Gemma Compose. |
| <a id="pt09"></a>PT09 — Exercise the complete Compose stack | PARTIAL | [Evidence](../reports/container-rehearsal.json) | Historical Phi3 build/start/restart and PG retention passed; two answerable timeouts. Gemma Compose was not run. |
| <a id="pt10"></a>PT10 — Restart without losing required state | PASS_WITH_SCOPE | [Evidence](../reports/final/native-bound-flow.json) | Two native answer records and two linked QA feedback records retain identical hashes after app restart. Historical PostgreSQL retention is separate. |
| <a id="pt11"></a>PT11 — Verify reviewer data and credential access | PARTIAL | [Evidence](../data/README.md) | Three public licensed snapshots included; no commercial key required. Anonymous exact-commit receipt follows publication. |
| <a id="pt12"></a>PT12 — Reconcile ingestion completeness | PASS_WITH_SCOPE | [Evidence](../reports/remediation-v2/corpus-coverage.json) | Three sources; 377 windows; 390 exclusions. Headings retained as metadata, table/figure interpretation excluded. |
| <a id="pt13"></a>PT13 — Check repeat loads and updates | PASS_WITH_SCOPE | [Evidence](../reports/checks.json) | Actual unchanged repeat load matches IDs/hash; immutable replace snapshots, no incremental-update claim. |
| <a id="pt14"></a>PT14 — Round-trip passage citations to the source | PASS_WITH_SCOPE | [Evidence](../reports/checks.json) | All retained windows round-trip exactly; tables/figures excluded; one actual browser source span also verified. |
| <a id="pt15"></a>PT15 — Validate dlt normalized relationships | NOT_APPLICABLE | [Evidence](../reports/../navigator/corpus.py) | dlt receives flat normalized chunk records; no child-table join is selected. |
| <a id="pt16"></a>PT16 — Test orchestration failure and rerun boundaries | NOT_APPLICABLE | [Evidence](../navigator/corpus.py) | No Kestra flow is selected; Compose dependency startup is assessed in PT09. |
| <a id="pt17"></a>PT17 — Check contracts across components | PASS_WITH_SCOPE | [Evidence](../reports/checks.json) | 186 checks pass without skips; synthetic fixtures isolated; real shipped-config transport/export/status checks retained. Model quality separate. |
| <a id="pt18"></a>PT18 — Challenge exact identifiers and filters | PARTIAL | [Evidence](../reports/retrieval-contracts.json) | Mode/source-filter and near-collision contracts pass; six-slice quality results still expose retrieval and answer failures. No blanket biomedical identifier precision claim. |
| <a id="pt19"></a>PT19 — Validate vector identity and search behavior | PASS_WITH_SCOPE | [Evidence](../reports/retrieval-contracts.json) | All vector rows aligned, finite normalized dimensions; exact rankings agree. No approximate index or persisted-vector claim. |
| <a id="pt20"></a>PT20 — Check English inputs, Unicode offsets and context limits | PASS_WITH_SCOPE | [Evidence](../reports/final/native-setup.json) | 377 encoder inputs with zero truncation; source offsets round-trip. Native server 4,096 context observed separately; no larger-window guarantee. |
| <a id="pt21"></a>PT21 — Hand-check metric and rank arithmetic | PASS_WITH_SCOPE | [Evidence](../reports/checks.json) | One-based MRR, zero-based RRF, missing hit and duplicate ranking fixtures checked; independent RRF sums in retrieval-contracts. |
| <a id="pt22"></a>PT22 — Audit evaluation questions and reference evidence | PARTIAL | [Evidence](../data/evaluation/questions-v2.json) | 60 exact source-anchored questions with required facts/qualifications; assistant labels remain provisional. |
| <a id="pt23"></a>PT23 — Prevent tuning leakage | PASS_WITH_SCOPE | [Evidence](../data/evaluation/questions-v2.json) | 42 development / 18 final; the final bank was readable/validated and is not blind. No final inference during this release work. Old 13 questions remain regression-only. |
| <a id="pt24"></a>PT24 — Compare multiple retrieval approaches fairly | PASS_WITH_SCOPE | [Evidence](../reports/final/selection-2026-09-07.json) | Same 42-question factorial and separate ablation support active hybrid top-10/title-0;26/35 fully covered. Label limitations and losses retained. |
| <a id="pt25"></a>PT25 — Demonstrate hybrid search with ablation | PASS_WITH_SCOPE | [Evidence](../reports/retrieval-contracts.json) | Both candidate branches and hand-checked fused scores recorded; separate branch ablation metrics saved. |
| <a id="pt26"></a>PT26 — Separate reranking evidence from bonus assumptions | PASS_WITH_SCOPE | [Evidence](../navigator/retrieval.py) | Active hybrid uses documented zero-based RRF k=50. Both branches and fused ranks retained; double credit remains unresolved. |
| <a id="pt27"></a>PT27 — Test query rewriting preserves intent | PASS_DIAGNOSTIC_ONLY | [Evidence](../reports/final/rewrite-diagnostic-review.json) | Twelve identical rewrites preserved intent and ranks but added time without benefit. Disabled; no answer-quality or bonus claim. |
| <a id="pt28"></a>PT28 — Prove the application loads the selected configuration | PASS_WITH_SCOPE | [Evidence](../reports/final/native-bound-flow.json) | Actual answers match full bound config hash, model digest, corpus and runtime. Generation status remains below quality approval. |
| <a id="pt29"></a>PT29 — Trace a grounded answer end to end | PASS_WITH_SCOPE | [Evidence](../reports/final/native-bound-flow.json) | EXA-01 useful and ABS-01 abstaining, one attempt each; six browser exports, QA feedback and restart verified. Not a new accuracy sample. |
| <a id="pt30"></a>PT30 — Handle absent, conflicting and irrelevant evidence | PARTIAL | [Evidence](../reports/release-quality/source-extract-complete-pilot-judgments.json) | Source-excerpt complete pilot has 8/12 acceptable answers and a critical irrelevant excerpt. Exact quotations do not establish relevance, completeness or preserved qualifications. |
| <a id="pt31"></a>PT31 — Compare final-answer approaches | PASS_WITH_LIMITATION | [Evidence](../reports/final/selection-2026-09-07.json) | Controlled pair complete 8/12 versus concise 6/12,critical 1 each; complete bound with explicit owner exception. Internal quality bar and full 42-question paired follow-up remain unmet. |
| <a id="pt32"></a>PT32 — Audit the automatic judge | CONDITIONAL | [Evidence](../docs/evaluation.md#answer-evaluation-and-judgment) | Automatic-judge calibration is required only if that route is used. Explicit assistant review is available; provisional review is not biomedical expert validation. |
| <a id="pt33"></a>PT33 — Bound and validate the agent tool loop | NOT_APPLICABLE | [Evidence](../reports/../docs/decisions.md) | Fixed flow; no model tool loop. |
| <a id="pt34"></a>PT34 — Evaluate agent trajectory as well as final text | NOT_APPLICABLE | [Evidence](../reports/../docs/decisions.md) | No claimed agent advantage over fixed RAG. |
| <a id="pt35"></a>PT35 — Trace UI or API interaction and feedback | PASS_WITH_SCOPE | [Evidence](../reports/final/native-download-check.json) | Six actual downloads match stored answers and exact source/export bytes; two answer-linked QA feedback records verified. |
| <a id="pt36"></a>PT36 — Isolate conversation state | PASS_WITH_SCOPE | [Evidence](../reports/checks.json) | Two AppTest sessions do not inherit an answer; feedback duplicates suppressed; single-turn UI only. |
| <a id="pt37"></a>PT37 — Exercise controlled end-to-end failures | PARTIAL | [Evidence](../reports/remediation-verification.json) | Read-outage warning and recovery passed AppTest; provider/schema failures covered with mocks; real PostgreSQL outage still untested. |
| <a id="pt38"></a>PT38 — Measure latency and account for all calls | PASS_WITH_SCOPE | [Native evidence](../reports/final/native-bound-flow.json), [rewrite evidence](../reports/final/rewrite-diagnostic-review.json) | 145 historical native + 3 historical container + 2 new native generation attempts, kept separate. Twelve additional rewrite calls, zero diagnostic generation. New generation 148.8s/51.0s; request 155.2s/51.8s; no retry or provider billing. |
| <a id="pt39"></a>PT39 — Verify feedback plus five actual charts | PASS_WITH_SCOPE | [Evidence](../reports/final/native-bound-flow.json) | Six rendered charts,2 stored requests and2 linked QA ratings before and after native restart. No researcher satisfaction. |
| <a id="pt40"></a>PT40 — Reconcile dashboard denominators | PASS_WITH_SCOPE | [Evidence](../reports/final/native-restart-browser.txt) | Scope qa/all contains 2 LLM requests, 2 ratings, 5,114 input and 34 output tokens; denominator is stored requests, not a research-use metric. |
| <a id="pt41"></a>PT41 — Preserve telemetry and distinguish synthetic data | PASS_WITH_SCOPE | [Evidence](../reports/final/native-bound-flow.json) | Native QA records survive restart; original historical PostgreSQL proof is separate. No fake user traffic. |
| <a id="pt42"></a>PT42 — Audit evidence honesty and completeness | PASS_WITH_SCOPE | [Evidence](readiness.md) | Historical versions, mocks, real runs, failed candidates, provisional labels and scoring uncertainty distinguished. Current English/package/link checks complement the evidence, not replace quality evaluation. |
| <a id="pt43"></a>PT43 — Rehearse README and demonstration | PASS_WITH_SCOPE | [Evidence](../reports/final/native-bound-flow.json) | Actual bound-config question, useful answer, refusal, exports, feedback and six charts reviewed in English; research utility is not measured. |
| <a id="pt44"></a>PT44 — Score each rubric row conservatively | PASS_WITH_SCOPE | [Evidence](../reports/../docs/readiness.md) | Core/practice/bonus/review requirements separate, evidence gaps explicit, no awarded total. |
| <a id="pt45"></a>PT45 — Freeze and revalidate the candidate release | PASS_WITH_SCOPE | [Evidence](../reports/final/release-gate.json) | Final freeze and 186 software checks; public-commit verification and clone receipts follow commit outside repo. |
| <a id="pt46"></a>PT46 — Prepare the real submission fields | BLOCKED | [Evidence](readiness.md#deadlines-and-actual-form-fields) | Required repository/SHA rules and optional fields verified in the live form/source. Existing course login and actual public release SHA unavailable; do not invent hours or contributions. |
| <a id="pt47"></a>PT47 — Verify saving and later hash updates | BLOCKED | [Evidence](readiness.md#deadlines-and-actual-form-fields) | OWNER ACTION ONLY: the owner saves the form, verifies success, reloads the repository/SHA and retains a private receipt. The assistant never saves the course form. |
| <a id="pt48"></a>PT48 — Recheck both deadlines with timezone evidence | PASS_WITH_SCOPE | [Evidence](readiness.md#deadlines-and-actual-form-fields) | Live UTC calendar checked: submission 7 Sep 23:00 UTC / 8 Sep 02:00 Jerusalem; reviews 14 Sep 23:00 UTC / 15 Sep 02:00 Jerusalem. Recheck immediately before saving. |
| <a id="pt49"></a>PT49 — Complete all assigned peer reviews at submitted commits | BLOCKED | [Evidence](readiness.md) | Three assigned peer reviews are required separately. No assignments inspected and no reviews submitted; this future obligation is not a pre-publication software test. |
| <a id="pt50"></a>PT50 — Confirm final status and certificate details | BLOCKED | [Evidence](readiness.md) | Live dashboard says 11 to pass, but no personal official grade or certificate record verified. Confirm account name and actual course outcome; no predicted score is an awarded score. |

## Next actions in dependency order

Follow [the current completion sequence](readiness.md#next-actions-in-dependency-order)
and [unchanged promotion controls](evaluation.md#change-promotion-with-regression-controls).
The agreed model/prompt comparison, whole-answer review and frozen development/final
split remain in force. An automatic judge, human scientific review, every optional
course tool and cloud deployment are not invented as prerequisite course rules.

Docker installation and the historical Phi3 rehearsal are complete. The final
route is native Gemma without new installations or Docker changes. The bounded
rewrite diagnostic completed before its cutoff with twelve calls and no observed
benefit. It left rewriting disabled and added no answer-generation samples.
Commit/publication/tag are authorized only after mandatory release checks pass.
Exact-commit verification follows publication. The owner alone saves the course
form and completes the three peer reviews; no official result is inferred.
