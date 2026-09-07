# RRF constant replay — iteration 023

**Decision: retain the active vector retriever.** None of the four predeclared
RRF constants improves reference coverage without losing coverage on another
answerable development question. No application configuration changed.

This extends the measured title-weight experiment, not the answer-generation
comparison. It executed **168 rank replays, zero fresh retrieval queries, zero
encoder calls and zero model calls**. All 42 development questions remain in the
record; retrieval metrics retain their 35-answerable-question denominator. The
seven absent-evidence questions have no gold retrieval targets and do not supply
abstention evidence merely because their ranks were replayed.

## Inputs and verification

- [Predeclared iteration](iterations/023-rrf-rank-replay.json), with its original
  plan copied and hashed inside the [complete results](rrf-rank-replay-023.json).
- [Original branch rankings](title-weight-retrieval-016.json), specifically
  `hybrid_title_0.0`, compared with `vector_incumbent` from the same experiment.
- [Reproduction code](rrf_rank_replay.py), importing the application's actual RRF
  function. Both branches have candidate depth 20; the final cutoff is 5.
- Course basis: [2026 homework 4, Q6 and Using this framework](https://github.com/DataTalksClub/llm-zoomcamp/blob/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/cohorts/2026/04-evaluation/homework.md#q6-tuning-hybrid-search),
  local lines 262–296. The taught grid is 1, 50, 100, 200. The course exercise
  optimizes MRR; our predeclared no-coverage-loss nomination rule is a project
  requirement, not an official grading threshold.

Before comparing candidates, k=50 reproduced **all 42 stored top-five lists,
every full fusion order and score, and the saved reference metrics exactly**.
Question identity/order, source/bank/config/corpus hashes, branch ranks and unique
IDs were checked. Every fused score has separately recorded lexical and vector
contributions. Fusion retains zero-based ranks; displayed ranks and first-hit MRR
are one-based. No input or frozen label was rewritten.

## Results

Mean reference coverage averages the matched fraction of each question's frozen
reference entries. It is not the percentage of correct answers, independent
publications or unique pieces of scientific evidence. Multiple required facts can
point to the same passage; the existing denominator remains explicit.

| Method | Hits / 35 | MRR@5 | Mean reference coverage | Fully covered / 35 | Questions gaining / losing coverage vs vector |
|---|---:|---:|---:|---:|---:|
| Active vector, saved baseline | 21 | 0.469524 | 0.566667 | 18 | — |
| RRF k=1 | 24 | 0.519048 | 0.647619 | 21 | 6 / 2 |
| RRF k=50 | 25 | 0.476667 | 0.671429 | 22 | 8 / 3 |
| RRF k=100 | 25 | 0.476667 | 0.671429 | 22 | 8 / 3 |
| RRF k=200 | 25 | 0.476667 | 0.671429 | 22 | 8 / 3 |

Equal metrics for k=50/100/200 do **not** mean identical retrieved lists. Some
top-five IDs/order differ; all lists are preserved in the results. No latency or
memory improvement can be inferred from replay computation.

| Slice | Questions | Vector coverage | k=1 coverage | k=50/100/200 coverage |
|---|---:|---:|---:|---:|
| Direct | 7 | 0.714286 | 1.000000 | 0.857143 |
| Paraphrase | 7 | 0.714286 | 0.500000 | 0.571429 |
| Exact identifiers | 7 | 0.857143 | 0.857143 | 1.000000 |
| Comparison | 7 | 0.261905 | 0.452381 | 0.357143 |
| Limitations | 7 | 0.285714 | 0.428571 | 0.571429 |
| Absent evidence | 7 | Not defined | Not defined | Not defined |

## Why the gains do not justify promotion

With k=1, DIR-01 and DIR-06 gain complete reference coverage, as does LIM-02.
COM-05 gains partial coverage, and COM-06 and COM-07 become fully covered. The
smaller constant also preserves the strong vector reference for DIR-07 which the
k=50 alternative loses. This supports the narrow mechanism in the hypothesis:
high single-branch ranks can survive better with k=1.

But PAR-01 falls from full coverage to one of two reference entries: the
electronic-record source remains at rank 2, while the explicit retrospective
design passage moves to rank 10. That passage was vector rank 5 and absent from
the lexical top 20. PAR-03 falls from full coverage to zero: its source describing
the 14/8 care-pathway groups moves from vector rank 3 to fusion rank 6. Both losses
are **ranking/cutoff losses of already available passages**, not missing ingestion.
The original source text and reference quotes were inspected; labels were not
broadened to make alternate passages count.

With k=50/100/200, losses remain DIR-07, PAR-01 and COM-02. In the k=50 trace,
DIR-07's cohort-variant passage is rank 6; PAR-01's required passages are ranks 6
and 12; COM-02's cohort passage is rank 7. COM-02's review passage is rank 23 and
was not covered by the vector top five either. Distinguish losing an existing
success from failing to recover a reference the incumbent already missed.

The larger-constant gains are DIR-01, DIR-06, EXA-01, COM-01, COM-05, COM-06,
LIM-02 and LIM-05. The lower paraphrase coverage is not compensated by a better
overall number under the frozen nomination rule.

## Engineering consequence and next action

RRF k alone is insufficient at the fixed five-passage cutoff. A separately
predeclared cutoff experiment can test whether retrieving more candidates
restores displaced evidence. More passages also mean a larger prompt, more
irrelevant context and potentially worse source attribution; existing small-model
failures make this a material risk. No cutoff increase is authorized by this
result as a runtime promotion. It needs its own comparable retrieval evidence,
actual context-budget check and downstream answer comparison.

R03 gains an inspected parameter comparison and a reason to retain the incumbent.
R04 gains no answer-quality proof; R08/R09 still lack a complete Compose rehearsal.
No point estimate or official point field was increased. The separately prepared
model-precision pilot still needs download authorization, and the application
still has no acceptable full-development generation winner.
