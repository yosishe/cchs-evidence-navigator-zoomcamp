# Local model feasibility — prepared, not executed

No new model has been downloaded or promoted. The active application still uses
Phi3 Q4 / evidence_first / vector. This report is evidence for a proposed
experiment, not a change to the research acceptance contract or an awarded score.

The [host observation](model-feasibility-observation.json) records 24 GiB physical
RAM and about 41 GiB available disk at observation. Physical RAM is not free RAM;
peak inference memory and latency remain unmeasured. Existing library versions are
recorded separately from the historical teaching environment. Docker rehearsal is
still a separate pending approval and execution gate.

## Proposed next experiment: Phi3 Mini Q8

The exact tag is `phi3:3.8b-mini-128k-instruct-q8_0`. Its published model layer is
4,061,222,368 bytes, approximately 4.1 GB, and its expected manifest digest is
`adc0589ce82eb5929896d7100a8f3a2a694a1251332d37f32b1cd5c72282f5a5`.
The existing Q4 manifest matches the installed baseline digest. Both registry
entries have identical template and stop-parameter blob hashes/content, verified
using small metadata requests only. [Official Q8 model](https://ollama.com/library/phi3:3.8b-mini-128k-instruct-q8_0),
[recorded registry metadata](phi3-precision-registry-metadata.json).

The first metadata attempt did not follow CDN blob redirects and failed hash
verification; the corrected read follows the public metadata redirect with a byte
cap and verifies each digest. That failure is preserved in the metadata record.
No model-layer bytes were requested. Public tag descriptions have inconsistent
context-window labels, so a label saying 128k or 4k is not proof of the actual
loaded context. Installed architecture/context metadata must be checked before
attributing any future improvement specifically to numerical precision.

The course implements Phi3 through Ollama in
[2024 qa_faq.py](https://github.com/DataTalksClub/llm-zoomcamp/blob/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/cohorts/2024/02-open-source/qa_faq.py).
It also implements a lower-precision loading choice in the
[2024 Mistral notebook](https://github.com/DataTalksClub/llm-zoomcamp/blob/bc7b6aad6b92a5611d3d37bf7521a363f3b9d398/cohorts/2024/02-open-source/huggingface-mistral-7b.ipynb),
physical cell 10. Applying the precision/resource trade-off to an exact Phi3 Q8
tag is our adaptation. The lecturer did not demonstrate this exact Q8 comparison
or guarantee better biomedical answers. It uses the same model family and serving
libraries; there is no new framework or commercial provider.

The [six-call plan](iterations/022-phi3-precision-pilot.json) uses the existing
`evidence_first` and `schema_first` prompts and three development questions. Both
matching Q4 arms already exist in the preserved six-call baseline; they are not
retried. Corpus, questions, retrieval,
output budget, temperature, JSON mode and final answer validation stay fixed.
The provider accepts only this exact additional tag, not arbitrary Phi3 variants;
digest mismatch and a missing model still block execution. The active config is
unchanged. Full raw outputs, semantic reviews, whole-answer veto and export checks
remain mandatory. A successful pilot only justifies wider development assessment.

**Trade-off:** approximately 4.1 GB additional model storage, potentially more
memory/latency, and uncertain benefit. The same model capacity may retain the same
reasoning failures. There is no evidence yet that Q4 quantization caused them.
Download authorization is absent; no model call has been made under this plan.

## Other actually taught alternatives

| Candidate | Exact teaching evidence | Why it is not the next automatic change |
|---|---|---|
| FLAN-T5 XL | 2024 `huggingface-flan-t5.ipynb`, physical cells 7–11: T5 tokenizer/model, source-only prompt and saved generated answer | The notebook's saved weight downloads total about 11.4 GB. Weights are absent locally; SentencePiece/Accelerate distributions are absent. Current compatibility and memory/latency need separate verification. Its seq2seq generation requires a different adapter and cannot inherit a passing score from the sample FAQ answer |
| Mistral-7B-v0.1 | 2024 `huggingface-mistral-7b.ipynb`, physical cells 9–13: 4-bit load, tokenizer and text-generation pipeline | This is the base model, not an automatically substituted Instruct release. Saved notebook downloads total about 14.48 GB. The historical accelerated environment is different from this Mac; quantized serving compatibility and additional dependencies remain unverified |
| Installed Gemma 3 12B | No demonstrated course implementation identified for this specific model in the current project source map | Installation alone does not make it course-grounded; it remains excluded |

The [FLAN-T5 model card](https://huggingface.co/google/flan-t5-xl) documents both
CPU and GPU loading, but does not establish quality on this corpus. The
[Mistral model card](https://huggingface.co/mistralai/Mistral-7B-v0.1) identifies a
pretrained base model. The current main
[bitsandbytes installation guide](https://huggingface.co/docs/bitsandbytes/main/en/installation)
lists macOS arm64 CPU support; it would be inaccurate to claim all Apple Silicon
use is impossible. The stable-version page failed to load in this check, and no
installed runtime validation was performed. Do not infer a working Mac 4-bit
application from a historical CUDA notebook or from that platform list.

Notebook code and saved outputs were read statically. No course shell cell,
login, package install, weight download or notebook inference was executed. These
alternatives do not expand the current application toolbox merely by appearing in
this report; each needs its own justified implementation and authorized setup.
