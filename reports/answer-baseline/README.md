# Final-answer baseline: one prompt, three development questions

**One approach has been evaluated on a small, deliberately selected diagnostic
sample. Answer quality is insufficient; no generation winner was selected.**

This package makes the preceding examiner's real outputs and explicit assistant
review available inside the project. The records were copied unchanged from the
6 September 2026 audit. Packaging generated **zero new model calls** and changed
no application code, model, prompt, corpus, reference labels or active setting.
These are the same calls described in that audit, not independent replications.

## Configuration and provenance

| Field | Value |
|---|---|
| Model / prompt | Local Ollama `phi3` / `evidence_first` |
| Model digest | `4f222292793889a9a40a020799cfd28d53f3e01af25d48e06c5e708610fc47e9` |
| Runtime code ID | `e675401ddae7adfb80548bb47e7ce2d9912fc5b0603030858069fccfc39ff011` |
| Config ID | `6c2fc0821246681a10c9b8f33789c6177ac32dc4a353dd7d34e52e413b61a5d2` |
| Retrieval | Selected vector retrieval, top 5, 750/150 character windows |
| Generation | Temperature 0, JSON object mode, 900 output tokens, 120-second timeout |
| Sample | `DIR-01`, `DIR-02`, `ABS-01`; all development questions |
| Review | Codex assistant; no biomedical expert review |

[Manifest and file hashes](manifest.json) bind the package to its originals.
[Raw results](results.json) retain question requirements, retrieved passages,
actual request messages, provider usage and output. Each [review](reviews.json)
refers to its answer ID and content hash. This is an examiner record format,
**not** a completed `evaluate-answers`/`select-generation` artifact. Do not pass
this three-question subset off as the full 42-question development evaluation.

## What was evaluated

The review examined schema validity, exact quotation/source agreement, semantic
support of each claim, coverage of the required facts, abstention and visible
limitations text. A real quotation is necessary but cannot establish that every
requested fact was answered. Empty claim lists do not establish safe prose.

| Question | Observed output | Source-based judgment | Decision implication |
|---|---|---|---|
| DIR-01: the Italian study's two aims | `insufficient_evidence`; reference passage absent from top 5 | No complete answer. Abstention is conservative for the supplied context, but the corpus contains the required passage. | Diagnose the reference miss before changing generation alone. Nearby discussion may be relevant despite incomplete labels. |
| DIR-02: cohort size and period | One supported claim about 22 patients; no 2000–2020 period | Partly complete: the first retrieved passage contains both requested details. | Prompt/output completeness needs improvement even with successful retrieval. |
| ABS-01: an intervention result not established by this corpus | `insufficient_evidence`, no claims | Correct abstention status; the limitations wording nevertheless presupposes the requested intervention was reported. | Evaluate all visible prose and avoid adopting unsupported question premises. |

| Measure | Numerator / denominator | Meaning and limitation |
|---|---|---|
| Schema-valid outputs | 3/3 | Mechanical validity only |
| Supported formal claims | 1/1 | One claim only; not whole-answer accuracy or correctness of free prose |
| Complete answers to answerable questions | 0/2 | Both question requirements must be addressed |
| Correct abstention status for absent evidence | 1/1 | Wording caveat remains; status alone is not a fully satisfactory answer |

There is no representative accuracy estimate, human satisfaction result or
statistical significance claim. The sample omits several development slices.
It was not held out from development, and it must not be used as a final test.

## Corroborating diagnostics, not extra benchmark questions

The [known-reference diagnostic](known-reference-diagnostic.json) supplied DIR-01's
exact reference passage while bypassing retrieval. The model produced the two
aims but omitted the required `exact_quote` fields; validation correctly rejected
the output. This shows that repairing retrieval alone would not guarantee a valid
answer. It does not add a successful retrieval result to the baseline denominator.

The [browser observations](browser-check.json) and [underlying journal](browser-events.jsonl)
include one repetition of DIR-02 through Streamlit. It again omitted the period.
The UI displayed the answer, citation and claim table; saved QA feedback belonged
to that answer; five required charts and a token chart were observed. Four
journalled requests used 7,540 input and 581 output tokens. Those counts exclude
the separate known-reference call and the project's separate nine-call pilot.

The export button was clicked, but completed browser download bytes were not
verified. Do not turn that observation into a download-success claim. QA feedback
describes relevance for this test and is not researcher satisfaction.

## Reproduce without replacing these records

First follow the [existing setup](../../README.md#local-setup). This package
installs or downloads nothing. The following optional replay makes three local
model calls through the same application function and writes a new runtime
directory. It leaves these published evidence files and the active configuration
unchanged. Run it only with the already-prepared local course model and encoder.
Different hardware/server settings can produce different outputs; preserve them.

```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 ENABLE_PAID_LLM=0 .venv/bin/python - <<'PY'
import os
from datetime import datetime, timezone
from navigator.common import ROOT, read_json, read_documents, load_config, digest, runtime_code_id, write_json
from navigator.retrieval import Retriever
from navigator.rag import run_request

package = ROOT / 'reports/answer-baseline'
manifest = read_json(package / 'manifest.json')
baseline = read_json(package / 'results.json')
config = load_config()
assert config['provider'] == 'ollama' and config['model'] == 'phi3'
assert digest(config) == manifest['config_id']
assert runtime_code_id() == manifest['runtime_code_id']
documents = read_documents()
assert digest(documents) == baseline['corpus_id']
stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
out = ROOT / 'runtime/baseline-replays' / stamp
os.environ['NAVIGATOR_RUNTIME'] = str(out)
engine = Retriever(documents, config)
records = []
for question in baseline['questions']:
    assert question['split'] == 'tuning'
    record = run_request(question['question'], engine, config,
                         use_llm=True, traffic_origin='qa')
    records.append({'question_id': question['id'], 'record': record})
    write_json(out / 'records.json', records)
    print(question['id'], record['status'])
print(out / 'records.json')
PY
```

The replay uses no gold passage as runtime context. Compare every output with the
same required facts and source quotations, record missing facts as missing, and
keep errors. A repeated `answered` status is not evidence that the omitted period
was repaired. The snippet was syntax-checked when packaging; no new replay ran.

## Rubric and next decision

The [official rubric](https://github.com/DataTalksClub/llm-zoomcamp/blob/main/project.md#evaluation-criteria)
has a one-point tier for evaluating one final-answer approach and a two-point
tier for comparing approaches and using the best. This package supplies evidence
for consideration under the first tier. Awarding a point remains the reviewer's
decision; packaging cannot improve the actual model outputs.

The [separate paired pilot](../experiments/answers-73a724cb-ac01-49e1-8937-d0aee751302f/results.json)
made nine of twelve planned calls and stopped. Its review is still pending.
It cannot establish a winner, and these baseline reviews do not complete its
missing pairs. Keep the active configuration until a course-grounded candidate
passes the [comparison and selection protocol](../../docs/evaluation.md).

The next useful experiment is a minimal complete JSON example and explicit
coverage of every requested fact, with the same retrieved context. Changing
context aliases, output length policy or model should be isolated experiments.
Preserve strict exact-quote validation, all failed attempts and source provenance.
No application promotion or new quality threshold was enacted by this package.
