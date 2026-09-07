# Adding publications without invalidating existing evidence

The active app still uses the original three-paper corpus. A separately staged
research candidate registers the fourteen additional publications requested by
the owner. Its source coverage, extraction checks and retrieval comparisons are
reported in [the intake ledger](../reports/corpus-expansion/intake.json).
It is not a selected release, an answer-quality result, or an additional grade.

## The decision sequence

Research need -> identity and access -> immutable source snapshot -> extraction
review -> isolated ingestion -> retrieval regression -> answer evaluation ->
researcher review -> release review -> deliberate promotion.

Keep the stable version available throughout this sequence. A new source can
change relevance, ranking, context size and whether a question is answerable.
Previously measured results remain results for their original corpus and code.

## 1. Register and verify each publication

Record the requested title, PMID, verified PMCID and DOI, journal and publication
dates. Match identifiers against the NCBI record and the actual full-text front
matter. Keep online and print dates separately when they differ. Deduplicate
publications by canonical identifiers; multiple formats are not independent
evidence. The fourteenth item in this request retains source-list ID `ART-015`.

Save the original bytes and SHA-256, acquisition URL/date, copyright/license,
authors, extraction scope and review state. Record an explicit blocked or partial
status when necessary. A PMC identifier or an open-access flag does not by itself
establish permission for every redistribution: inspect the article's license.
Use the [official BioC service](https://www.ncbi.nlm.nih.gov/research/bionlp/APIs/BioC-PMC/)
and [per-article reuse guidance](https://pmc.ncbi.nlm.nih.gov/tools/openftlist/).

For the fourteen requested publications, the local candidate has ten full-text
BioC sources and four **abstract-only** sources: PMIDs `40816914`, `40610826`,
`20208042` and `36289132`. All fourteen local PDFs were located and hashed. The
four full PDF bodies are not indexed in this pilot. Representative PDF checks
found interleaved columns, tables, figure captions and running text; preserving
the PDFs does not prove that this extraction is usable.

The candidate includes noncommercial, no-derivatives, author-manuscript and
copyright-restricted material. It is kept outside the public project package.
Publication rights need a separate source-by-source decision. This local staging
decision is not a legal determination that all derived outputs can be shared.

## 2. Prepare traceable passages

Reuse the existing `navigator.corpus.prepare` contract. Every included manifest
entry needs a unique `source_id`, `raw_file`, SHA-256, title, year, article type,
source URL and license. The BioC document identity must match the source ID.
Extra manifest fields preserve acquisition provenance and extraction scope.

Some upstream BioC documents use a numeric or `unknown` document ID while their
front matter unambiguously identifies the publication. This batch makes an
explicit derived snapshot with a canonical ID after PMCID and DOI agreement.
Keep the upstream response and both hashes. Never repair an identity by guessing
from a filename or similar title.

This batch also maps abstract heading types to the existing parser's heading
type, and marks reviewed supplementary notices, editorial highlights/synopses
and administrative footnotes as excluded. All passage text and original offsets
remain unchanged; a reversible transformation ledger records each metadata edit.
Original source bytes remain available separately. No runtime parser was changed.

The four abstract-only entries use exact NCBI abstract-section text in a project
BioC envelope. `ABSTRACT ONLY` is visible in article type and section headings.
Envelope offsets locate the derived abstract, **not a PDF page**. Do not answer a
question about unavailable tables or full-text methods from these abstracts.

Before admitting a PDF full body, inspect reading order against rendered pages;
record physical pages and exact extracted spans. Separate table rows, figure
captions and footnotes from prose. Excluded information remains a coverage gap.
Do not repair biological identifiers, numbers, signs or negations silently.

Expected evidence row:

```json
{
  "source_id": "PMC_EXAMPLE",
  "source_version": "<derived-snapshot-sha256>",
  "passage_index": 12,
  "start_in_passage": 0,
  "end_in_passage": 83,
  "content": "<exact source substring; illustrative record>",
  "section_heading": "Results",
  "article_type": "primary study",
  "source_url": "<verified publication URL>"
}
```

The lengths and identifiers above are placeholders, not a valid test fixture.
For an actual row, require `content == passage[start:end]`, verify the source
hash and preserve the citation through retrieval, answer validation and export.

## 3. Stage an isolated package

Run [the staging tool](../tools/stage_corpus_expansion.py) from the active project
using a prepared intake manifest. Use a **new destination outside the project and
outside the intake directory**; the two may be siblings. Supply real absolute
paths in place of these placeholders:

```bash
python3 tools/stage_corpus_expansion.py \
  --manifest /absolute/research/intake/manifest.json \
  --destination /absolute/research/candidate-project
```

The tool verifies sources before writing, excludes private environment files,
Git history, runtime state and model/PDF artifacts, and preserves the runtime
code identity. It carries the baseline publications into the combined manifest
without changing their raw bytes. It marks retrieval and generation **unselected**
and points to `data/evaluation/expansion-development.json`, which must initially
be absent. Old question banks and reports remain historical copies.

Read `reports/corpus-expansion-staging.json` in the candidate. Confirm its
candidate config/corpus hashes and source list. The receipt proves staging;
it does not certify the supplied manifest's license decisions or semantic labels.

## 4. Run ingestion and retrieval checks in the candidate

Use an already prepared Python environment and the pinned encoder cache; this
step needs no new model download or paid provider. Run from the candidate root.
Set `NAVIGATOR_RUNTIME` to its separate runtime directory and
`NAVIGATOR_MODEL_CACHE` to the verified existing cache. Offline settings must
remain active for this rehearsal:

```bash
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
python -m navigator ingest
python -m navigator prepare-encoder
```

Here `python` must identify the existing project environment with its dependencies.
Do not run the commands in the active checkout. Ingestion uses dlt/DuckDB replace
inside the candidate runtime. Save counts, per-source exclusions, corpus and
document hashes, load IDs, timing and the pinned encoder revision. Re-run ingestion
once and verify identical document content and counts rather than duplicated rows.

Check that every article has usable evidence, every ID is unique, source hashes
and quote offsets resolve, and old evidence rows are preserved. Count token
truncation with the actual pinned tokenizer; a character limit is not a token
limit. Record every affected passage and whether required evidence lies outside
the encoded prefix. A successful embedding call is not sufficient.

Run three retrieval methods on identical questions and parameters: lexical,
vector and the course's zero-based RRF hybrid implementation. Preserve ranked
IDs and both branch rankings, not just averages. Report two different checks:

- **Baseline evidence retention:** rerun the old answerable development questions
  with their unchanged source anchors. Inspect wins and losses individually. Old
  anchors are not exhaustive labels for the enlarged corpus; a newly retrieved
  valid source must be reviewed before calling it wrong or adding it as gold.
- **New-source smoke checks:** ask source-grounded probes for each new article,
  verify source identity, exact quote recovery and metadata filters. These probes
  are development diagnostics authored from the articles, not a blind benchmark
  or proof of useful answers.

## 5. Rebuild the evaluation boundary

Revisit all old unanswerable development questions: added evidence may change
their labels. Keep old records unchanged; create corpus-specific new labels with
supporting quotations, required facts, material qualifications and abstention
reasons. Use semantic groups to keep paraphrases together. Record which questions
were exposed. Never relabel an exposed final set as a fresh blind test.

Keep the candidate's normal expansion question-bank path absent until the
development bank has been reviewed. Store smoke probes under a different path.
An old bank must fail the new corpus-hash check. The current validator does not
automatically perform the scientific review or enforce every license constraint.

After retrieval defects are understood, compare allowed model/prompt alternatives
on identical candidate contexts. Log every attempted call, including timeout,
invalid structure and refusal of answerable questions. Review exact citations,
semantic support, all required facts, qualifications and appropriate abstention
separately. Diagnose retrieval versus generation with explicitly labelled reference
contexts. Do not replace useful-answer requirements with syntactic validity or a
weighted score that hides a critical failure.

## 6. Preserve research meaning and human review

Keep human patients, postmortem cases, mice, cells and organoids distinct. Separate
primary findings from a review's discussion of another study. Keep patient QoL
and caregiver-burden denominators separate; do not apply pooled spinal-cord-injury
case-report rates to CCHS. Date the 2010 policy statement explicitly.

The supplied tag PDF is an input list and prior annotation artifact. Its proposed
terms and approval states do not automatically modify this project's tag vocabulary
or establish scientific conclusions. All evidence/tag exports remain pending
researcher review. Expansion may reveal useful connections; it does not validate
a mechanism, treatment, hypothesis or discovery.

## 7. Promotion and course evidence

Promotion requires a concrete reviewed package that contains:

1. An identity/license/extraction ledger with every partial or excluded source.
2. Candidate ingestion and restart evidence, pinned encoder and model identities,
   and reconciled disk/memory/call accounting.
3. Retrieval comparisons with examined losses and corpus-specific development
   labels; a documented decision with alternatives and trade-offs.
4. Useful, supported and complete model answers meeting the existing quality
   contract, followed by the declared final evaluation procedure.
5. A real candidate browser check: question -> model answer -> sources -> export
   download -> saved answer -> linked feedback -> monitoring. Test activity must
   remain labelled as test activity.
6. Candidate Compose build/start/restart and retained rows. Historical three-paper
   Compose results do not certify the enlarged corpus.
7. English-only release/link/secret checks and evidence links for the exact release
   version. Keep publication and course submission under the owner's control.

Do not promote a candidate merely because it has more papers, a better retrieval
average or more software tests. The original generation candidate already lacked
a passing useful-answer result; corpus expansion does not silently close that gap.

## Trade-offs and revisit triggers

| Decision | Benefit | Cost or limitation | Revisit when |
|---|---|---|---|
| Separate candidate package | Protects live configuration, data and experiment history | Duplicate small package and separate evidence paths | A selected, reproducible candidate is ready for explicit promotion |
| Official BioC prose first | Structured sections and exact passage provenance | Tables/figures and some publisher material remain outside the parser | A research question requires excluded evidence |
| Explicit abstract-only intake for four sources | All requested publications are discoverable without corrupted PDF prose | Many methods, results and qualifications remain unavailable | Page/object-aware extraction passes a documented review |
| Keep original retrieval parameters for first comparison | Isolates corpus expansion as the changed variable | Parameters may not suit the larger corpus | Per-question failure diagnosis supports a specific alternative |
| Source-authoring smoke questions | Quickly detects missing sources and broken identity/quotes | Biased toward known article language and coverage | Replace or supplement with researcher tasks and fresh held-out questions |
| Leave active release unchanged | Preserves established behavior and honest grading evidence | User does not yet get expanded live answers | Retrieval, answer, browser and reproducibility gates all pass |

These are project adaptations of the course's ingestion, retrieval, evaluation
and reproducibility principles. See [course provenance](course-sources.md),
[evaluation rules](evaluation.md), [design decisions](decisions.md), and the
[official rubric](https://github.com/DataTalksClub/llm-zoomcamp/blob/main/project.md#evaluation-criteria).
The course does not award points merely for the number of publications.

## Agent continuation prompt

```text
Continue the isolated CCHS corpus-expansion candidate described in
docs/corpus-expansion.md and reports/corpus-expansion/intake.json. Verify the real
active and candidate paths before work. Preserve the active three-paper manifest,
configuration, raw sources, questions, runtime identity and historical reports.
Read the local intake ledger, transformation receipts and retrieval diagnostics.

Resolve extraction and retrieval failures before answer-generation experiments.
Four sources have abstract-only coverage; never claim their full PDFs are indexed.
Review all 17 tokenizer overflows and the per-question ranking losses. Test only
course-supported alternatives; label project adaptations. Use the fixed encoder
revision and existing local provider without automatic downloads or paid fallback.
Keep source/PMID/DOI identity, exact quotes, qualifiers and population/model context.

Create reviewed corpus-specific development references, revisiting old no-answer
labels. Keep source-authored smoke tests distinct from independent quality tests.
Do not use old final questions for tuning or call exposed questions blind. Count
every model attempt, including errors. Review support and completeness separately.
Do not choose a candidate that fails the established useful-answer contract.

After a candidate passes, demonstrate its own browser/export/feedback/monitoring
and Compose restart flow. Audit English documentation, source licenses, secrets,
relative links and reproduction from the exact release. Explain each decision's
source, alternatives, trade-offs, experiment, measured result and revisit trigger.
Present the concrete release package for the owner's publication review. Never
promote, commit, publish or submit merely because an experiment improved an average.
```
