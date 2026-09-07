# Retrieval cutoff and fresh-runtime verification — iterations 024–025

**A ten-passage candidate improves retrieval coverage, but it is not yet a
selected answer configuration.** Title-weight-zero RRF with k=1 and cutoff 10
fully retrieves the frozen reference entries for 25/35 answerable development
questions, compared with 18/35 for the active vector cutoff 5. No question loses
reference coverage against that active baseline. The actual retriever reproduced
this result. Keep the application unchanged until downstream answer and context
capacity checks demonstrate that the larger input is useful.

## What was executed

Iteration [024](iterations/024-retrieval-cutoff-capacity.json) predeclared three
cutoffs (5, 10, 20) within two fixed ranked lists: vector and title-zero RRF1.
It performed **252 saved-rank replays**, including the two cutoff-five baselines,
without a new query or model call. The baseline IDs and metrics matched their
original artifacts exactly. [Complete replay](retrieval-cutoff-capacity-024.json)
and [diagnostic code](retrieval_cutoff_capacity.py) retain every question and
reference position/classification.

Iteration [025](iterations/025-fresh-cutoff-retrieval.json) then executed **84
fresh offline retrieval queries**, 42 for each cutoff-ten candidate, through the
actual `Retriever` and shared `prepare_context` path. Every returned ID list,
reference match, metric and content-character count matched the replay. Both
encoder reports resolved the pinned revision, the same 377-window corpus and zero
truncated encoder inputs. The process exited successfully; no run remains pending.
[Actual output and traces](fresh-retrieval-025/results.json),
[execution code](fresh_cutoff_retrieval.py).

The encoder loaded from the existing local cache with downloads disabled. There
were **zero generation or rewrite calls**, zero installs and no active config
change. These runs do not repeat or improve the existing 101 generation receipts.
The 42-question development bank includes seven absent-evidence questions;
retrieval quality retains the 35-answerable denominator and provides no new
abstention-quality evidence. No final questions were used for this computation.

The course basis is [2026 evaluation homework, Using this framework](https://github.com/DataTalksClub/llm-zoomcamp/blob/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/cohorts/2026/04-evaluation/homework.md#using-this-framework),
which teaches evaluating the number of returned results with fixed ground truth.
The numerical cutoffs, reference-coverage criterion and smallest-eligible-cutoff
rule are our predeclared project choices, not course recommendations or grading
thresholds. RRF k and lexical weights were fixed within each stratum, not retuned
after seeing these results.

## Coverage and cost

| Retrieval / final cutoff | Hits / 35 | MRR at cutoff | Mean reference coverage | Fully covered / 35 | Mean content characters per question |
|---|---:|---:|---:|---:|---:|
| Active vector / 5 | 21 | 0.469524 | 0.566667 | 18 | 2,260.48 |
| Vector / 10 | 26 | 0.490612 | 0.666667 | 20 | 4,365.36 |
| Vector / 20 | 30 | 0.496918 | 0.790476 | 25 | 8,721.10 |
| Title-zero RRF1 / 5 | 24 | 0.519048 | 0.647619 | 21 | 1,852.00 |
| Title-zero RRF1 / 10 | 26 | 0.528571 | 0.733333 | 25 | 3,820.98 |
| Title-zero RRF1 / 20 | 32 | 0.538640 | 0.871429 | 29 | 8,060.76 |

Increasing a cutoff mechanically makes more references reachable. It does not
measure precision or prove that a model uses them correctly. Counts above retain
the existing reference-entry definition; multiple facts may cite one passage.
The smallest eligible cutoff in each method is 10, so 20 was not nominated for
the next runtime check merely because it gives the largest recall number.

The fresh run also measured the serialized context including publication metadata:

| Candidate | Mean context characters | Maximum context characters | Total of 42 query preparation times |
|---|---:|---:|---:|
| Vector / 10 | 9,370.48 | 11,361 | 0.167448 seconds |
| Title-zero RRF1 / 10 | 8,790.33 | 10,314 | 0.212390 seconds |

These character counts exclude the question, instructions, chat template and
reserved output. **They are not model-token counts and do not prove fit in the
allocated generation context.** Encoder nontruncation concerns individual MiniLM
inputs and cannot establish Phi3 context capacity. Setup/encoding timings are
stored separately. Sequential cached execution is not a controlled latency
benchmark, and none of the query times includes model generation.

## Gains, losses and remaining misses

Vector / 10 improves DIR-01, COM-01, COM-05, LIM-02 and LIM-07 over vector / 5.
It retains all five original passages by construction. Title-zero RRF1 / 10
improves DIR-01, DIR-06, COM-01, COM-05, COM-06, COM-07 and LIM-02 over vector / 5.
It also recovers the PAR-01 and PAR-03 passages lost by RRF1 / 5 in iteration 023.

The candidates are **not interchangeable**. Hybrid / 10 fully covers four of the
seven comparison questions, while vector / 10 fully covers none. However, vector
/ 10 recovers one of LIM-07's two reference entries, while hybrid / 10 recovers
neither. The other LIM-07 entry is outside both saved branch candidate lists.
Hybrid / 10 has worse paraphrase MRR than vector / 10 despite equal reference
coverage there. These are real trade-offs, not hidden failures or evidence that
one method wins every metric.

| Hybrid / 10 incomplete cases | What the saved branch/fusion traces establish | Appropriate next diagnosis |
|---|---|---|
| PAR-02, PAR-05 | Required passage is lexical rank 11, absent from vector top 20, fused rank 20 | Lexical candidate quality/ranking; more final slots can recover it, but add context |
| EXA-01 | Required passage is vector rank 19, lexical rank 11, fused rank 13 | Ranking/cutoff loss |
| COM-02 | Review reference is vector rank 12 and fused rank 23; cohort reference is already retrieved | Multi-source coverage remains incomplete even at hybrid cutoff 20 |
| COM-04 | Required passages are fused ranks 20 and 30 | Ranking and finite candidate/context budget |
| COM-03, LIM-01, LIM-06 | Required entries are absent from both branch top-20 lists, but exist in the frozen corpus | Investigate query/representation/candidate retrieval; final cutoff alone cannot fix them |
| LIM-05 | Required passage is vector rank 20, lexical rank 14, fused rank 17 | Ranking/cutoff loss |
| LIM-07 | One required entry is vector rank 7/fused rank 15; another is absent from both candidate lists | Two distinct failures; one cutoff loss and one candidate miss |

All missing references were checked for presence in the current corpus and their
original exact quotes. This does not make the labels exhaustive: alternative
unlabeled relevant passages may exist. No label was added to rescue a metric,
and no primary-study evidence was inferred from a review's reference list.

## Decision and next experiment

**REVISE; no runtime promotion.** Retain vector / 5 while testing generated answers.
The next focused pilot should hold the installed Phi3 model, current
`evidence_first` prompt, output budget and evaluation rules fixed, and compare the
two cutoff-ten retrieval policies. Include DIR-01 (newly available aims), PAR-01
(recovered study-design references), COM-01 (multi-source coverage) and ABS-01
(unanswerable control). Reuse matching original baseline receipts where available;
do not rerun failed baseline answers to seek a favorable sample. Predeclare and
verify the exact requests before making the eight candidate generation calls.

Review every claim, required fact/qualification, nonanswer, limitation and export.
Keep actual model input counts and serving context evidence separate from these
character counts. A useful pilot only justifies the full paired development
comparison; it does not replace selection, final assessment, browser downloads or
Compose reproduction. If added context harms answers, retain the incumbent and
the failed candidate outputs. The separate Q8/Docker approval requests remain
pending and are not implied by these offline retrieval runs.

R03 now has fresh executed candidate traces and an inspected no-loss coverage
comparison against the active baseline. R04 still lacks a usable selected
generator. No official point field, historical score estimate or readiness gate
was increased just because retrieval coverage improved.

Follow-up: [iteration 026](cutoff-answer-026/report.md) executed the proposed eight
local calls and rejected both answer candidates after complete review. The
retrieval gains above remain measured evidence; they did not yield an acceptable
generator or change the active application configuration.
