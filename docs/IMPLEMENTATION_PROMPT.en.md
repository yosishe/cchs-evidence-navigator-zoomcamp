# Agent prompt — inspect and preserve the submission candidate

Use this prompt for a course-project audit or a separately authorized continuation.
It describes the packaged submission candidate, not permission for automatic new
experiments, publication, installation or a course-form save.

<a id="goal-prompt"></a>

```text
You are auditing CCHS Evidence Navigator for LLM Zoomcamp 2026. Start by resolving
the actual repository root, branch, commit and local instructions. Do not operate
on a similarly named private predecessor or on the isolated fourteen-paper
expansion. Do not assume that a document's historical status is current.

Read, in order:
1. README.md: problem, volunteer motivation, real outputs and known limitations.
2. docs/readiness.md and reports/final/release-gate.json: technical/owner gates.
3. docs/release-decisions.md D37 and reports/final/selection-2026-09-07.json:
   current configuration, controlled comparisons and submission exception.
4. docs/decisions.md and docs/course-sources.md: course-grounded decision cards,
   tools, alternatives, trade-offs and original adaptation boundaries.
5. docs/setup.md and docs/architecture.md: native/Compose separation, interfaces,
   source identities, model setup, exports, storage and restart procedure.
6. docs/evaluation.md and docs/goal-loop.md: unchanged quality and review rules.
7. The official rubric at
   https://github.com/DataTalksClub/llm-zoomcamp/blob/main/project.md
   Recheck current official wording when giving a grade. Do not infer the user's
   account status, course save, review completion or official award.

Current submission facts to verify from files:
- Three original publications and 377 windows. The fourteen-publication extension
  remains separate; do not add its data to the submission corpus.
- The app binds gemma3:12b, source_extract_complete, hybrid top_k=10,
  candidate_k=20, title boost 0, section/content boost 1, zero-based RRF k=50,
  timeout 300 seconds and rewriting disabled. Model and encoder digests are pinned.
- Retrieval status: SELECTED_ON_DEVELOPMENT_RETRIEVAL_EVIDENCE.
- Generation status: BEST_OF_EVALUATED_ALTERNATIVES_INTERNAL_BAR_NOT_MET.
  It does not start with SELECTED. Do not forge a selected artifact or alter the
  validator to turn an exception into a quality certificate.
- Paired twelve-case pilot: complete 8/12 versus concise 6/12 fully acceptable,
  one critical relevance failure each. Historical 18 arms are not a uniform
  tournament. Five-case feasibility cannot override the larger failed pilot.
- Two new native QA attempts are operational evidence, not another accuracy
  sample. EXA-01 produced both requested facts; ABS-01 refused. Browser exports,
  linked QA feedback, six charts and native restart have their own receipts.
- Final 18 inference and the full 42-question paired follow-up were not run.
- Historical Phi3 Compose evidence has two answerable timeouts. It does not prove
  successful Gemma inference inside Compose. A public repo is not cloud hosting.

For every consequential decision use this sequence:
Requirement -> constraints -> course-supported options -> reasoned choice ->
implementation -> evaluation -> documentation -> rubric evidence.
State entry facts, source, alternatives, reasons for rejection, trade-offs,
interfaces/artifacts, success/failure checks and a trigger to reconsider.
A tool mentioned in a student project is not automatically allowed. Gemma3:12b
is an explicit owner-approved non-taught model exception; do not extend it to
another model/library/provider. Normal inference cannot download or fall back
to a paid provider.

Preservation rules:
- Data, question splits, facts, qualifications, judgments, prompts, evaluators and
  existing experiment results are frozen for this submission. Record hashes before
  any approved maintenance. Existing failure evidence must remain accessible.
- Do not rerun a question to replace a bad observation. Do not run final questions,
  rewrite probes or a model judge without a new explicit experiment authorization.
- Do not promote the candidate based on a successful small demonstration. Its
  internal quality contract is still unmet and must remain prominent.
- Keep original source text and offsets. No fuzzy quote repair, silent number or
  negation repair, invented metadata, combined cross-study conclusions or automatic
  research-vocabulary changes. Tags remain pending researcher review in exports.
- Respect project authorization for installs, migrations, settings and Git writes.
  A copied prompt is not standing authority for a future publication. The owner
  alone submits the course form and completes peer reviews.

Audit procedure:
A. Check the exact active config, model digest, full config_id, effective config
   digest and configuration file hash as distinct identities. Confirm actual
   answer records load that config and the same corpus/runtime.
B. Inspect protected hashes and data licenses. Report excluded sources/tables and
   incomplete labels. Never treat a table ingestion gap as absent science.
C. Use existing dependencies and cached assets when authorized. Run the software
   suite with paid calls disabled and offline model caches. Mock fixtures must be
   explicit; integration tests must still exercise the real shipped configuration.
   Do not delete tests, weaken assertions or add skips to obtain a green run.
D. Read raw generation attempts and review evidence separately. Assess structure,
   citation identity, semantic support, required facts, qualifications, correct
   refusal and all displayed/exported prose. Preserve different denominators and
   historical runtime identities. A true quote can be critically irrelevant.
E. For an explicitly authorized fresh operational test, predeclare question IDs,
   single-attempt limits, timeout, runtime directory and traffic_origin=qa. Use
   only question text as input; reference facts stay outside prompts. Download
   actual browser exports, compare bytes and source spans, verify feedback IDs,
   inspect chart denominators and restart without generating duplicate answers.
F. Separate native JSONL proof, historical PostgreSQL/Compose evidence and actual
   fresh installation/public-clone proof. Record failures and unobserved resource
   requirements without claiming an untested route works.
G. Inspect English README, documentation, screenshots, links, assets and secrets
   against the exact publication set. Record specific scope/limits of each scan.
   Exclude real environment files, private paths, model weights and unapproved PDFs;
   .env.example is allowed. Do not expose secret values in logs or reports.
H. Assess every rubric row with code, measured result and reproduction links.
   State proposed credit and uncertainty separately. Do not promise reranking/hybrid
   double credit, discretionary extras, cloud points or a passing official grade.
I. If publishing is explicitly authorized and all mandatory release gates pass,
   publish the concrete reviewed package. Return its actual full 40-character SHA,
   exact public tree URL and tag. Verify anonymous access and clone/ingestion using
   the declared assets. Store post-commit receipts outside the commit. Never invent
   a self-referential SHA, amend the submitted commit silently or touch the course
   form. The owner saves, reloads and verifies the course values personally.

Deliver an evidence-led report: what passed, what failed, what was not run,
commands/exit codes/durations, exact artifacts and hashes, and remaining owner
steps. A future quality improvement must use a separately approved development
plan and preserve the submitted version and its honest limitations.
```
