# Final submission-candidate evidence

This directory documents the 7 September 2026 release preparation. A passing
operational release check does not mean the model passed the internal quality
contract: the selected development pilot remains **8/12 fully acceptable, with
one critical relevance failure**. The owner accepted this disclosed exception.
The final eighteen-question inference test was not run.

| Evidence | What it establishes |
|---|---|
| [Release gate](release-gate.json) | Mandatory packaging and operational checks; publication follows their pass |
| [Selection](selection-2026-09-07.json) | Bound model, full/file/effective configuration identities, paired comparisons and rejected alternatives |
| [Before-change freeze](phase0-freeze.json), [recheck](frozen-input-recheck.json) | Preserved source, benchmark, runtime, prompts and historical evidence; named authorized changes only |
| [Test-fixture review](test-fixture-review.json), [software checks](../checks.json) | Explicit mock configurations, retained behavioral assertions, 186 tests with no skips |
| [Independent review](independent-review.json) | Separate agent review of test changes, selection claims, documentation and native evidence; not scientific certification |
| [Native setup](native-setup.json), [preflight](native-preflight.json) | Fresh ingestion into an isolated runtime using existing dependencies and cached encoder |
| [Predeclared demo](native-demo-plan.json), [actual flow](native-bound-flow.json) | EXA-01 and ABS-01 once each; useful source excerpt and correct abstention |
| [Download check](native-download-check.json), [download bytes](native-downloads/) | Six real browser downloads matched to stored answers and sources |
| [Stored events](native-events.jsonl), [restart browser state](native-restart-browser.txt) | Two answers and two QA ratings retained; six monitoring charts after native restart |
| [Native provider receipts](native-provider-attempts/) | The two actual generation attempts, raw outputs, tokens and timings |
| [Screenshot review](screenshot-review.json) | English visual checks, distinguishing current and historical screenshots |
| [Rewrite declaration](rewrite-diagnostic-plan.json), [raw run](rewrite-diagnostic.json), [review](rewrite-diagnostic-review.json) | Twelve exact-input echoes, unchanged ranks, extra latency, no answer generation; keep disabled |
| [Compose scope](compose-final.json) | Gemma was not rehearsed inside Compose; earlier Phi3 results remain historical |

`phase0/environment.json` and `phase2/pilot-1-summary.json` predate this final
execution. They were present in the initial freeze and are retained unchanged as
historical evidence. Current environment observations are in
[environment-preflight.json](environment-preflight.json); those earlier files do
not describe current Docker availability or the newly bound configuration.

Generation, rewriting and software fixtures have different denominators. The
diagnostic's 8/10 retrieval Hit@10 is not the pilot's 8/12 answer-quality result.
The new two-case demonstration is operational evidence, not an accuracy estimate.
No researcher satisfaction, independent scientific validation or course grade is
claimed. Native storage is JSONL; historical PostgreSQL receipts describe the
separate Phi3 container rehearsal.

Public-commit verification and clone receipts are created after publication and
kept outside the commit they identify. Course-form saving and peer reviews remain
owner actions. This package does not claim they have happened.
