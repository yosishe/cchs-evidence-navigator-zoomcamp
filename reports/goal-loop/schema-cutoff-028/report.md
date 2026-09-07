# Iteration 028 — enforced fields improve structure but expose incorrect refusals

**REJECT both candidates. No runtime promotion or additional points claimed.**
The schema fixes all seven missing-top-level-field failures from iteration 026.
Nevertheless, neither retrieval policy delivers a complete supported answer on
any of its three answerable questions or an acceptable whole nonanswer on ABS-01.
Required fields are insufficient evidence of a useful research application.

The [predeclared protocol](../iterations/028-schema-missing-fields.json) tests
eight new local Phi3 calls against the eight saved iteration-026 receipts.
Within each retrieval policy only `response_format` changes. Canonical source
content, the exact request messages, model digest, prompt, temperature and output
budget are verified unchanged. All contexts are reused: zero fresh retrieval
queries, no reference labels in generation, no final inference and no retries.

| Outcome | Baseline without schema | Fixed schema |
|---|---:|---:|
| Objects containing all required top-level fields | 1/8 | 8/8 |
| Outputs passing canonical validation | 0/8 | 6/8 |
| Complete supported answerable responses | 0/6 | 0/6 |
| Acceptable whole nonanswers | 0/2 | 0/2 |
| Input tokens | 28,061 | 28,061 |
| Output tokens | 706 | 1,607 |

All six now-valid outputs are refusals. Four contain a source-contradicting denial
or an unsupported intervention premise, one has an unresolved characterization
of the guideline context, and one makes a supportable but unhelpful observation
that the sources do not explicitly compare themselves. The baseline blocked all
eight outputs; allowing these six to reach the visible-prose stage is a practical
regression even though validation errors decrease. The unchanged whole-answer
review rejects them. More generated fields also more than double output tokens
in this small comparison; this is not a general latency or cost forecast.

| Context policy / question | Diagnosis and source-based decision |
|---|---|
| Vector / DIR-01 | Denies explicit aims despite Italian passage 17 enumerating both; mentioning related topics while denying their role is not a correct answer |
| Vector / PAR-01 | Invalid status/claims relationship, invented/full-version IDs and empty quotes are blocked; no answer from passages 19/21 |
| Vector / COM-01 | Omits available retrospective-record evidence; guideline 13 remains missing in this context. The restriction of guideline material to Italy is unsubstantiated, so prose support remains unresolved |
| Vector / ABS-01 | Abstains but presupposes a randomized intervention reported in the Italian study |
| Hybrid / DIR-01 | Both aims appear in the raw draft, but passage identity and exact quotation remain wrong; the complete-looking draft is correctly blocked |
| Hybrid / PAR-01 | Denies study-design details despite passages 19/68 and electronic records in 21 |
| Hybrid / COM-01 | Refuses to synthesize the separately available Italian methods and guideline 13. A literal absence of an explicit comparison in the source text does not answer the user's comparison request |
| Hybrid / ABS-01 | Abstains but again presupposes an intervention reported in the study |

Every canonical export payload is empty. That is internally consistent with
refusals/errors, not a successful research artifact or a verified download.
Relevant source passages were re-inspected; preparation also confirms every saved
hit against the unchanged canonical corpus. The original iteration-026 source
review remains historical evidence. All semantic judgments are provisional agent
review, not expert validation. No schema implementation or evaluator was altered
after viewing these results.

The following paths preserve every raw response, primary judgment, mandatory
whole-answer veto and source/configuration identity:

- Vector: [results](../../experiments/answers-0cb52db7-1c7d-493e-ae6c-1a8d635c80a2/results.json), [primary review](../../experiments/answers-0cb52db7-1c7d-493e-ae6c-1a8d635c80a2/reviews.json), [whole review](../../experiments/answers-0cb52db7-1c7d-493e-ae6c-1a8d635c80a2/whole-answer-review.json).
- Hybrid: [results](../../experiments/answers-ca46397a-76c1-40f0-bda3-adfc0399b600/results.json), [primary review](../../experiments/answers-ca46397a-76c1-40f0-bda3-adfc0399b600/reviews.json), [whole review](../../experiments/answers-ca46397a-76c1-40f0-bda3-adfc0399b600/whole-answer-review.json).
- [Paired comparison and exact counts](comparison.json), [preparation](preparation.json), [execution](execution.json), [vector exports](vector_10-exports-reviewed.json), [hybrid exports](hybrid_title_0_rrf_1_10-exports-reviewed.json).

The disabled implementation remains an auditable experimental option. Revisit
it only with an explicitly justified generation/model experiment and the same
semantic, completeness and export gates. Adding stricter field constraints or
increasing the number of reviewed failures alone cannot earn full R04 credit.
Full paired development, selected-version final testing, browser export/storage
proof and clean Compose rehearsal remain unproven. The separately prepared Q8
download and Docker setup still need owner authorization.
