# Cutoff-ten answer pilot — iteration 026

**Decision: reject both candidates for application promotion.** Better retrieval
coverage did not produce a complete validated research answer. Each candidate
delivered 0/3 acceptable answerable responses and 0/1 acceptable nonanswer. All
eight completed local outputs were rejected by the existing mechanical validator.
No reference, acceptance rule, model or active configuration changed.

The [predeclared plan](../iterations/026-cutoff-answer-pilot.json) tests only the
retrieval policy. Both candidates use the same installed Phi3 Q4 digest, current
`evidence_first` instructions, temperature zero, JSON-object mode and 900-token
output limit. Four matching vector/cutoff-five baseline requests reconstruct
exactly with the current message builder; their preserved results were reused,
not rerun. There were eight new context-retrieval queries and **eight new model
calls**, not twelve. No paid call, model download or installation occurred.

## Actual results and original evidence

| Candidate | Answerable accepted / 3 | Nonanswers accepted / 1 | Mechanical output failures / 4 | Evidence |
|---|---:|---:|---:|---|
| Vector / 10 | 0 | 0 | 4 | [Raw results](../../experiments/answers-61c1c04b-6628-4313-8bdd-af0e0b15244a/results.json), [primary review](../../experiments/answers-61c1c04b-6628-4313-8bdd-af0e0b15244a/reviews.json), [whole-answer review](../../experiments/answers-61c1c04b-6628-4313-8bdd-af0e0b15244a/whole-answer-review.json) |
| Title-zero RRF1 / 10 | 0 | 0 | 4 | [Raw results](../../experiments/answers-f88d7be4-47e4-4a00-9e84-16f4a8c0eadd/results.json), [primary review](../../experiments/answers-f88d7be4-47e4-4a00-9e84-16f4a8c0eadd/reviews.json), [whole-answer review](../../experiments/answers-f88d7be4-47e4-4a00-9e84-16f4a8c0eadd/whole-answer-review.json) |

Every raw output, all 41 unique retrieved windows, the application-visible error
note and both canonical export payloads were inspected. Exports are empty because
the outputs are invalid. Their mechanical consistency is not a useful research
result. Review judgments remain provisional assistant judgments, not independent
human validation. [Review comparison](review-comparison.json).

| Question | Vector / 10 | Title-zero RRF1 / 10 | What the result means |
|---|---|---|---|
| DIR-01: two study aims | Refusal JSON omits `limitations` | Raw text contains both aims, but uses publication/version strings as passage IDs and changes the quoted wording | Retrieval now finds the aims. A useful draft fragment does not establish a valid cited answer |
| PAR-01: study design and records | Omits `claims`; also says design evidence is absent despite the retrospective and electronic-record passages | Refusal JSON omits `limitations`, despite both references being retrieved | Generation/structure failure remains after retrieval availability is established |
| COM-01: study versus guideline method | Refusal JSON omits `limitations`; this context still lacks the exact guideline evidence/clinical-experience reference | Refusal JSON omits `limitations` even though both required references are present | Distinguish the vector candidate's remaining reference gap from the hybrid candidate's generation failure |
| ABS-01: unsupported intervention result | Refusal JSON omits `limitations` | Refusal JSON omits `limitations` | Intended refusal is not a delivered valid corpus-bounded nonanswer |

Seven outputs omit a required top-level field. In the remaining hybrid DIR-01
output, the first quotation adds a comma absent from Italian passage 17; the
second changes the opening of passage 54 from “The study” to “Our study”. Both
`evidence_id` values are a full publication/version string rather than an actual
window ID. No ID guessing, quote repair or fallback evidence attachment was used.

The relevant raw DIR-01 text is a limited positive diagnostic: the model can now
state both aims when that passage is retrieved. It does not overcome the invalid
citations or supply a deployable answer. The preserved baseline had one mechanical
error among these four cases, compared with four for each new candidate; total
acceptable responses remain zero. Keep that structural regression visible.

## Context and execution accounting

| Candidate / question | Input tokens | Output tokens | Recorded completion reason |
|---|---:|---:|---|
| Vector / DIR-01 | 3,318 | 25 | stop |
| Vector / PAR-01 | 3,268 | 44 | stop |
| Vector / COM-01 | 3,510 | 25 | stop |
| Vector / ABS-01 | 3,725 | 18 | stop |
| Hybrid / DIR-01 | 3,568 | 519 | stop |
| Hybrid / PAR-01 | 3,332 | 25 | stop |
| Hybrid / COM-01 | 3,369 | 25 | stop |
| Hybrid / ABS-01 | 3,971 | 25 | stop |

The two postflight checks observed an allocated 4,096-token context. The
[server observation](server-context-observation.json) correlates eight completed
requests by timestamp/order and token counts; each has a `truncated = 0` release
record. The raw outputs also have normal stop reasons. This does not support
blaming these particular failures on observed prompt truncation. It also does not
prove that every longer question or the full 900-token output allowance fits.
There is little remaining context space in the longest observed completion.

The initial [sandbox metadata check](../iteration-026-preflight.json) failed
because local network access was denied. The server was still listening. The
[authorized host check](../iteration-026-preflight-host.json) succeeded with the
same installed digest. No server restart or settings change was performed.
The [execution record](execution.json) and terminal process result establish that
both arms finished. There is no active pilot to resume and no failed answer to
retry for a more favorable result.

## Next focused repair: structured output, with semantics still independently checked

The recurring missing-field failure suggests using the course's schema-backed
output method. [Module 4's ground-truth lesson](https://github.com/DataTalksClub/llm-zoomcamp/blob/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/04-evaluation/lessons/02-ground-truth.md)
defines a Pydantic output type and passes it to `responses.parse`; the
[evaluation helper](https://github.com/DataTalksClub/llm-zoomcamp/blob/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/04-evaluation/code/evaluation_utils.py)
uses the same method for typed results. These exact source implementations were
read statically; no paid course example or retry helper was executed.

[Ollama's current documentation](https://docs.ollama.com/capabilities/structured-outputs)
describes JSON-schema output through its OpenAI-compatible `response_format`.
Mapping the taught schema method to the existing local Chat Completions adapter
would be **our compatibility adaptation**, not a claim that the course demonstrates
that exact local wire format. No new model/framework is implied.

This mechanism is not implemented or tested in this checkpoint. Before using it:
predeclare the schema and a small controlled comparison; preserve the original
smaller retrieval context, prompt, model and output budget; record the actual
schema sent in the call receipt; retain raw output and existing strict validation.
Do not confuse a schema-conforming object with a supported or complete answer.
Wrong citations, altered quotations, false limitations and omitted scientific
facts must still fail. A successful pilot only justifies the full development
comparison and later end-to-end/final gates.

Keep vector / 5 active. The separately prepared Q8 experiment and Compose
rehearsal still require their outstanding approvals. Current R03 retrieval
evidence remains useful; R04 has no selected acceptable generator. No score or
official point field is increased by this unsuccessful pilot.
