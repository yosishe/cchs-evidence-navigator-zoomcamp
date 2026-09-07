# Iteration 027 — schema constraints did not improve the incumbent-context answers

**REJECT for quality promotion.** Six new local Phi3 calls reproduce all six
historical baseline raw outputs exactly. There is no acceptable complete answer
under either prompt. The active configuration is unchanged; official points are
null. This is an application experiment, not a final assessment.

The [predeclared decision](../iterations/027-schema-constrained-generation.json)
changes only the generation `response_format` from `json_object` to a fixed
`json_schema`. Three saved vector/top-five development contexts, two prompts,
the same Q4 weights, temperature zero and 900-token output budget are retained.
Preparation verifies current canonical source text and exact message equality
against the six preserved baseline calls. There are no new retrieval queries.

The fixed schema contains the existing answer fields and claim fields. It does
not constrain the content of a quotation, entailment, question coverage or the
relationship between status and nonempty claims; the existing validator and
whole-answer review continue to enforce those separate requirements. The
configuration flag is optional, generation-only and false by default. Rewriting
retains its own JSON-object route. Invalid settings, provider failure and output
truncation do not trigger retries or a less constrained fallback.

| Question | `evidence_first` | `schema_first` |
|---|---|---|
| DIR-02: cohort count and period | Supported count/retrospective claim; 2000–2020 omitted despite passage 19 | Supported background from passage 54; count and period omitted |
| PAR-01: retrospective records or randomized experiment | Incorrect refusal denies design/record evidence available in passages 19/21/68 | `answered` with no claims is rejected; raw prose also denies available evidence |
| ABS-01: unsupported intervention premise | Correct status, but visible prose presupposes an intervention reported in the study | Rejected title-as-quote and wrong-source claims; no correct nonanswer |

All six raw objects already contain the schema's required typed fields, including
in the historical baseline. Therefore this pilot does **not** demonstrate that
the provider actually enforced missing fields: the grammar had no observed
field-shape violation to prevent. It also does not establish that the provider
ignored the option. Iteration 028 separately tests the eight preserved cutoff-ten
contexts, where seven previous outputs actually omitted top-level fields.

The two displayed DIR-02 claim exports were inspected alongside all 11 unique
retrieved windows. They preserve their incomplete answer and pending review;
they do not cure omitted facts. The other four canonical exports are empty.
No browser download or researcher feedback was tested here. Source review remains
provisional agent review; reused judgments for identical outputs are explicitly
identified and rebound to the new answer/export hashes.

Evidence: [raw results](../../experiments/answers-760b413c-69a7-4d62-ae94-f41098570e78/results.json),
[primary review](../../experiments/answers-760b413c-69a7-4d62-ae94-f41098570e78/reviews.json),
[mandatory whole-answer review](../../experiments/answers-760b413c-69a7-4d62-ae94-f41098570e78/whole-answer-review.json),
[comparison and actual token counts](comparison.json), [exports](exports-reviewed.json),
[preparation](preparation.json), [execution](execution.json),
[provider metadata](postflight.json), [15 focused tests](targeted-tests.log),
[121 full-suite checks](full-tests.log).

The course basis is [2026 structured output](https://github.com/DataTalksClub/llm-zoomcamp/blob/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/04-evaluation/lessons/02-ground-truth.md)
using Pydantic with Responses.parse. The local Chat Completions schema mapping is
our compatibility adaptation, supported by the [provider documentation](https://docs.ollama.com/capabilities/structured-outputs).
A fixed dictionary avoids a new direct dependency or installation; it is not
claimed to reproduce the exact lecturer API call. No source notebook was run.
