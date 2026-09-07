> **Historical record.** This document describes its earlier runtime and approval state. For the submission candidate, use [current release evidence](release-status.md), [D37](release-decisions.md#d37--submission-candidate-with-an-explicit-quality-exception) and [setup](setup.md). Earlier pending items are not current-state assertions.

# Historical remediation record

The active configuration, corrected scoring interpretation and remaining work are in
[remediation v2](review-remediation-v2.md). The material below describes the earlier
corpus and execution state; its paid-model prerequisites and scores are historical.

# Examiner-review remediation and route to maximum supported credit

Updated 2026-09-06. This is an implementation/evidence record, not an official grade.
The reviewed baseline was `4fc74d7b7ec9850312d8f3d9b787f7f4aa08bd0a`.
The original external examiner report is preserved; this document records the subsequent changes.

## Changes and acceptance evidence

| Review finding | Change | Verification / remaining limit |
|---|---|---|
| F01: model overwrites identity and sources | Exact top-level and claim schemas; copy only the three answer fields; deep-copy application metadata | Regression fixtures reject foreign identity, mode, origin, usage and source fields; original provider usage and evidence remain intact |
| F02: dashboard read crashes | Read/aggregation failures display a bounded warning and recover on rerun | AppTest simulates outage then recovery without a traceback or leaked exception details |
| Additional cache defect found by regressions | Cache the retriever only; construct storage from the current runtime/backend | Temporary-ingestion/UI tests pass after an outage test; storage no longer follows an unrelated cached environment |
| F03: no measured answer comparison | Added a no-call plan, both answerability strata, unique checkpointed runs, review templates and validated review summaries | Workflow contracts tested. **No provider run or answer-quality score exists yet** |
| F04: small, provisional retrieval benchmark | Ran the declared 12-configuration RRF grid on tuning data only; built a researcher review packet | Incumbent retained: no justified improvement over Hit@5=5/7 and MRR=0.5476. Existing exposed test stays 2/4; no new held-out claim |
| F05: QA counted as users | Explicit origin on new answer/feedback records; origin and mode filters; historical unknown origin kept separate | Five charts observed in browser using labeled QA activity. No researcher-satisfaction claim |
| F06: incomplete research export | Separate passage and claim CSVs retain question/answer/config/corpus/source identities, URL, version and offsets; exact claim quotations visible in UI | CSV parse/write round-trip tests include special characters and formula defense. Browser download event did not expose a verifiable output file |
| F07: unverified Compose/PostgreSQL | Existing full Compose remains the selected deployment path; concrete clean-environment procedure below | Docker absent; no build, service restart or cloud deployment claimed |
| F08: limited scientific scope | Added year, source version, population/model and URL to model context; provided 43 review rows for eight tuning questions | Source corpus and labels unchanged. Researcher review, correction checks and wider coverage remain pending |

Dependencies did not change. No model was downloaded, no package was installed,
and no paid model call was made during this remediation. The cached local model
was not substituted for the course-backed configuration.

## Evidence links

- [Automated checks](../reports/checks.json): exact count, skips, output and external limitations.
- [Remediation verification](../reports/remediation-verification.json): source/code hashes and completed checks.
- [Browser observation](../reports/browser-remediation.json): actual QA request/feedback, chart scope and limitations.
- [RRF grid](../reports/retrieval-grid.json): all candidates and per-question rankings; no test-driven promotion.
- [Researcher packet JSON](../reports/retrieval-review-packet.json) and [CSV](../reports/retrieval-review-packet.csv).
- [No-call answer plan](../reports/answer-plan.json): eight questions, two prompts, at most 16 calls and 14,400 output tokens. Input tokens are additional; this is not a dollar-cost estimate.
- [QA origin correction](../reports/qa-origin-correction.json): one known pre-fix automated test reached the development journal. Its origin was corrected to QA; the original journal was preserved locally and no events were deleted.

The existing raw-source hashes, question labels, active retrieval configuration and
previous evaluation reports remain unchanged. Older reports describe their original
run and do not certify the modified code. The current verification record identifies
the new code by file hashes while the changes await a commit.

## Why this improves the grade without inventing evidence

The strongest immediate opportunity is completing the core rubric: real final-answer
comparison (up to 2 points) and feedback plus five usable charts (up to 2 points total).
The fifth required chart now measures retrieved-passage counts, which exposes empty
or changing context. A sixth token-usage chart appears only when actual provider usage
exists. Neither passage count nor QA feedback is mislabeled as answer quality.

Under the prior examiner's other assumptions, the repaired monitoring supports a
provisional structural assessment of **17/26**; completing and using a measured prompt
comparison could support **19/26** (18 core + 1 hybrid). These are conditional assessments,
not points awarded by the course, and container/live-model verification remains necessary.

The remaining seven possible points are separate: reranking 1, rewriting 1, cloud 2,
and discretionary extras up to 3. Do not assume all seven are available automatically:

- The taught optional reranking example uses RRF, which this project already uses
  for hybrid fusion. Double credit is unresolved; no unrelated cross-encoder was added.
- Module 1 demonstrates model-reformulated search-tool queries. A bounded rewrite
  experiment is a possible later course-backed route, but requires real calls,
  identifier/intent preservation and an observed benefit before activation. An unused
  rewrite function would not establish this credit.
- Cloud deployment must be a real deployment with authorized infrastructure and
  a tested course-compatible stack. A private GitHub repository is not deployment.
- Discretionary points require the examiner's judgment. The source-preserving claim
  table, failure recovery and researcher review workflow are concrete candidates for
  discussion, but require demonstrated utility; no fixed bonus is claimed.

The original problem remains appropriate. Expanding into an ontology, clinical NLP
framework or an untaught research system would enlarge scope without resolving the
missing answer-quality evidence.

## Execute the answer comparison after authorization

1. Configure a key locally and agree a dollar budget. Never put a key in the repository,
   report or chat. Read `reports/answer-plan.json` before enabling calls.
2. Export the authorized environment variables in the terminal (`.env` is not loaded
   automatically in the local shell path). Re-run the no-call plan:

```bash
.venv/bin/python -m navigator plan-answers
.venv/bin/python -m navigator evaluate-answers --split tuning
```

3. The command prints a unique run directory. Each response is checkpointed, and the
   process stops after the first generation/validation error. Retain the failed run;
   any further run has a new ID and consumes additional budget. No automatic retries.
4. Copy the run's `review-template.json` to a named review file. For every response,
   inspect the exact question, retrieved context, raw answer and reference evidence.
   Fill reviewer identity/kind, relevance, each claim's support label, correctness of
   abstention, and a reason. `human`, `assistant` and `llm_judge` are different kinds;
   never call an assistant's judgment human review.
5. Validate and summarize the completed review:

```bash
.venv/bin/python -m navigator review-answers reports/experiments/answers-RUN/results.json reports/experiments/answers-RUN/review-completed.json
```

6. A complete review compares acceptable-response rates, with the denominator and
   claim counts visible. An acceptable answerable response must be relevant and have
   every claim supported; an unanswerable question must be correctly declined.
   These are the project's declared review criteria, not invented course thresholds.
   Missing judgments, altered outputs and incomplete/error runs cannot produce a winner.
7. Record the selected prompt, rejected alternative, cost/latency tradeoff and summary
   hash in `docs/decisions.md`; update `configs/app.json`. A tied result needs a stated
   decision. This is deliberately a reviewable decision, not an automatic config edit.
8. Verify the running app's new config identity, then reserve newly reviewed questions
   before any claim of independent final testing. Existing test questions are exposed.

## Container acceptance procedure — not yet executed

Use an authorized machine with Docker/Compose and an isolated checkout of the final
commit. Follow the README's explicit local key/password setup. Run `docker compose
up --build`; verify the one-off ingestion completes before the app starts and the DB
is healthy. In the browser ask a question, inspect sources and record its answer ID,
then save feedback. Restart the app and DB without deleting volumes, repeat the storage
read, and verify that exact ID and feedback survive. Confirm the corpus hash and
selected config agree with the evaluation evidence. Test a controlled DB outage and
recovery. Save the actual build/version/health and persistence results. Do not report
this procedure as executed until a real environment has passed it.

Public reviewer access, exact-commit submission and three peer reviews remain separate
release requirements. They are not performed by this remediation.
