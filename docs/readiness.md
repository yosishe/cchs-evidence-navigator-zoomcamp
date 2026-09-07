# Submission readiness and verified course requirements

**Submission candidate — 7 September 2026.** The shipped configuration is the
measured Gemma/source-extract-complete/hybrid-top-10 candidate, under the owner's
explicit disclosed submission exception. **The internal quality bar remains
unmet: 8/12 fully acceptable pilot answers and one critical relevance failure.**
The final 18-question inference test was not run. This document does not claim a
saved course form, an official grade or scientific review.

The new [native operational flow](../reports/final/native-bound-flow.json) proves
one useful EXA-01 answer and one correct ABS-01 abstention, six actual matching
browser downloads, two linked QA ratings, six charts and unchanged records after
a native application restart. [186 software checks passed without skips](../reports/checks.json).
The [final release gate](../reports/final/release-gate.json) owns package status;
[selection evidence](../reports/final/selection-2026-09-07.json) owns the bound
configuration and its disclosed limits.

Public exact-commit verification and clone/ingestion receipts are created after
the release commit and kept outside it. The owner alone logs into the course,
saves the form and completes assigned reviews. Earlier platform observations below
were recorded on 7 September; the final release procedure does not access the
course platform or infer account eligibility. The recorded passing setting was
11, not this project's awarded grade or a guarantee of acceptance.

Use the [50-check audit](pre-submission-audit.md), [rubric evidence](release-status.md#rubric-to-evidence-route),
[frozen internal quality contract](goal-loop.md) and [setup](setup.md). Historical
reports remain unchanged and describe their own configurations and dates.

## What is required by the course

| Requirement | Verified rule and current status | Evidence or action |
|---|---|---|
| Original individual project | Original CCHS literature project; owner identifies this as the first intended submission. Course adaptations are attributed. No previous course-account history was verified. | [Source map](course-sources.md), [data manifest](../data/manifest.json). Reuse of somebody else's project, a passed attempt or a previous-cohort/other-course project is prohibited. |
| Appropriate, accessible data | Three public literature snapshots are included with source identities and attribution. They are not the prohibited lecture/homework FAQ corpus. Tables and figures remain documented exclusions. | [Data and reuse terms](../data/README.md). Preserve source licenses and third-party exceptions. |
| English explanation | README, current project docs, source code, fixtures and screenshots have been reviewed for the owner's English-only release. | The official guide specifically requires an English README; the owner's package-wide condition is stricter. |
| Public repository and fixed version | Publication follows mandatory release gates. The exact submitted tree must be anonymously readable; its receipt follows the commit. | Use the canonical HTTPS web URL and full commit SHA; see the checker below. |
| Functional application and scored features | Native bound-config ingestion, useful answer, abstention, exports, feedback, charts and restart have new evidence. Historical Phi3 container answerable calls timed out; Gemma Compose execution is unproved. | [All nine core rubric rows and bonuses](release-status.md#rubric-to-evidence-route). These are scored criteria, not a demand to implement every course module. |
| Account and on-time submission | OWNER ACTION: use the existing account and verify saved form values. Earlier required-field/server checks did not identify an account or establish eligibility. | Log in with the existing course account, then verify the actual record after saving. |
| Passing score and peer reviews | The earlier dashboard observation recorded 11 to pass. Three assigned peer reviews must also be completed. Homework is optional for certification. | [Certification](https://datatalksclub.github.io/docs/courses/zoomcamp-logistics/certification/) and [peer-review rules](https://datatalksclub.github.io/docs/courses/zoomcamp-logistics/peer-review/). No reviews are claimed as completed. |

The [official rubric](https://github.com/DataTalksClub/llm-zoomcamp/blob/main/project.md#evaluation-criteria)
contains nine core rows worth up to 2 points each: **18 core points**. Hybrid,
reranking and rewriting add up to 3; cloud adds up to 2; discretionary additions
add up to 3: **26 project points maximum**. Review points are separate. Cloud and
discretionary bonuses are not mandatory passing conditions. RRF/hybrid double
credit remains the examiner's interpretation, not a promised two-point award.

The [course project guide](https://datatalksclub.github.io/docs/courses/llm-zoomcamp/project/)
requires an English README and explains the expected original, useful application.
The course does not prescribe our 60-question bank, two-model experiment,
zero-critical-failure promotion rule, automated judge or biomedical expert review.
Those are either project choices or unselected alternatives. The project must
still demonstrate and explain the features for which it claims credit. AI use
is [permitted by the course](https://datatalksclub.github.io/docs/courses/zoomcamp-logistics/ai-usage/);
the student remains responsible for understanding the submitted work.

## Deadlines and actual form fields

The earlier [attempt-3 page](https://courses.datatalks.club/llm-zoomcamp-2026/project/project3)
and its [UTC calendar](https://courses.datatalks.club/llm-zoomcamp-2026/calendar.ics)
were checked on 7 September. The calendar explicitly uses UTC `Z` timestamps.

| Event | UTC | Asia/Jerusalem |
|---|---|---|
| Attempt-3 project submission | 7 September 2026, 23:00 | **8 September 2026, 02:00** |
| Attempt-3 peer reviews | 14 September 2026, 23:00 | **15 September 2026, 02:00** |

Calendar `DTSTART` is the deadline. The calendar event's later `DTEND` is not an
extra submission window. The general project document describes two attempts;
the live 2026 platform explicitly offers attempt 3. Use the cohort platform for
this logistics difference. Anonymous "Not submitted" text is not the owner's
personal submission history. Recheck the live form immediately before saving.

The browser footer identifies platform version `20260831-144515-5cef603`. We read
its public source statically; no course-server code was executed or modified.

| Field or condition | What to enter or verify |
|---|---|
| Existing account | Use the account already enrolled in this course. This session has not identified its login provider. |
| Repository URL — required | `https://github.com/yosishe/cchs-evidence-navigator-zoomcamp`, only after it exists publicly. No `.git` suffix, private link or local path. |
| Commit ID — required | The actual full 40-character SHA returned by `git rev-parse HEAD` after the final release commit. Never a placeholder, branch name or SHA from the private predecessor. |
| Hours spent — optional | The owner's truthful hours, if supplied. A blank value is accepted; do not invent it from assistant wall time or token usage. |
| Learning-in-public links — optional | Only genuine, relevant public links, within the form's displayed limit. Leave blank when none exist. |
| FAQ contribution — optional | A genuine matching contribution if applicable. Do not insert an example or unrelated link. |
| Certificate name | Verify the existing name is correct English. A blank update preserves the account default; it does not prove that default was checked. |

The server's [model fields](https://github.com/DataTalksClub/course-management-platform/blob/5cef603/courses/models/project.py)
require a URL and nonempty commit string of at most 40 characters. **The server
does not resolve that string to a real commit.** The full hexadecimal SHA and
exact-tree verification are our additional protection against a technically
accepted but unusable submission.

The [URL validator](https://github.com/DataTalksClub/course-management-platform/blob/5cef603/courses/validators/custom_url_validators.py)
requires HTTP 200. It tries HEAD with a 3-second connection/read-inactivity timeout
and falls back to GET only for 403, 405 or 501. A redirect, inaccessible repository
or network failure can reject the form. Actual acceptance also depends on the
server's collecting-submissions state and the authenticated account.

The [save handler](https://github.com/DataTalksClub/course-management-platform/blob/5cef603/courses/views/project_submission_edit.py)
validates before saving. A button click is insufficient: verify the saved success
state and reload the exact repository/SHA fields. Keep a local receipt with time,
course/attempt and saved values; omit account identifiers from public reports.

## Checks already performed and gates still open

| Gate | Result and scope | Remaining boundary |
|---|---|---|
| Frozen inputs | [Pre-change inventory](../reports/final/phase0-freeze.json) and [release recheck](../reports/final/release-gate.json) | Data, runtime, evaluators, prompts and historical reports stay unchanged; only three permitted audit reports refresh |
| Software | [186 checks, zero skips](../reports/checks.json); explicit mock configs plus real shipped-config binding tests | Mock outputs do not establish model quality |
| Retrieval binding | [Measured hybrid/top-10/title-0 config](../reports/final/selection-2026-09-07.json) | Provisional incomplete labels and per-question losses disclosed |
| Native operation | [EXA-01 and ABS-01 once each](../reports/final/native-bound-flow.json) | Operational proof, not an accuracy estimate |
| Browser exports and feedback | Six matching downloads; two linked QA ratings; six charts; unchanged records after restart | Native JSONL route; no researcher-satisfaction claim |
| Internal generation quality | NOT MET: 8/12 pilot and one critical LIM-01 failure | Owner accepted a disclosed submission exception; original evaluator and judgments unchanged |
| Compose | Historical Phi3 build/setup, 172 Linux checks, abstention, exports and PostgreSQL retention proved | Two answerable timeouts; bound Gemma not run in Compose |
| Final assessment | Zero final-split inference calls | Final bank was readable/validated; not blind; not used for tuning or inference here |
| Package | [Language/secrets/assets](../reports/release-migration/public-package-audit.json), [links](../reports/release-migration/link-audit.json), real English screenshots | Scans have the stated limits; no all-possible-secrets guarantee |
| Public target | Commit, public repo, main push and v1.0.0 authorized after mandatory checks | Verify actual public 40-character commit and fresh clone; keep post-commit receipts outside repo |
| Course save and reviews | OWNER ACTION, not performed by the assistant | Save/reload repository and SHA; then complete three assigned peer reviews by their separate deadline |


## Exact public-target test after publication

This command is prepared, **not a successful live access receipt**. Run it only
after a real release commit is publicly available. The shell obtains the actual
SHA; do not type a made-up value.

```bash
release_commit=$(git rev-parse HEAD)
uv run python tools/verify_submission_target.py \
  https://github.com/yosishe/cchs-evidence-navigator-zoomcamp \
  "$release_commit"
```

The checker rejects wrong targets before networking, uses no credentials or
environment proxies, follows no redirects, and verifies public metadata plus the
exact commit and tree. It makes at most five requests, uses the platform's
3-second connect/read-inactivity timeout and caps each API JSON body at 1 MiB.
The byte cap is a project limit, not a course rule. It does not impose a hard
wall-clock deadline or verify model quality, a course save or certification. A
timeout/404 is an unverified result, not proof that a repository is private.

Keep this post-publication receipt outside the commit it identifies to avoid a
self-referential release hash. Re-run if the SHA, visibility or repository changes.

## Next actions, in dependency order

1. Inspect the final release-gate report and known quality limitation. Publication
   stops if a mandatory software, useful-demo, abstention, export, persistence,
   source-preservation or package check fails.
2. After publication, use the actual repository URL and full 40-character SHA
   from the delivery receipt. Verify the anonymous exact tree and the clone smoke
   result. Tag `v1.0.0` is convenient navigation, not a replacement for the SHA.
3. The owner opens the official attempt-3 form, checks the existing course account
   and certificate name, enters the repository/SHA and only truthful optional
   information, and saves. Reload and verify the saved values. A successful GitHub
   push is not a successful course submission.
4. Keep a private receipt of the course save. Complete three assigned reviews of
   the assigned commits by their separate deadline. No review or award is inferred.

The historical quality failure and unrun final set remain disclosed after
publication. Subsequent research improvement needs a separate development plan;
do not silently amend the submitted commit, force-push or replace its tag.
