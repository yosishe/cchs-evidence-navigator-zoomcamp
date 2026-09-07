# Current extraction note

The fourteen-paper expansion is an isolated research candidate; this manifest
and the active three-source corpus remain unchanged. See the
[expansion workflow](../docs/corpus-expansion.md) and
[per-article intake status](../reports/corpus-expansion/intake.json).

The raw snapshots and original 13-question file are preserved. The current
extraction has 377 windows and 390 exclusions (93 headings retained as metadata,
297 other excluded/empty passages). Seventy-eight headings were previously indexed.
The active 60-question source-anchored bank is `evaluation/questions-v2.json`; its
labels are assistant-authored and provisional. Tables remain excluded, even where
BioC contains XML. See [coverage audit](../reports/remediation-v2/corpus-coverage.json).

## Original acquisition record

# Corpus and permitted reuse

`manifest.json` is the source inventory. Each included raw JSON preserves the BioC
response exactly, with its SHA-256 and attribution/license text. Read the individual
license, including noncommercial and third-party exceptions where present. The
repository code does not grant a different license to article content.

Seed publications:

- Trang et al. (2020), *Guidelines for diagnosis and management of congenital central hypoventilation syndrome*, PMID 32958024, PMCID PMC7503443, DOI 10.1186/s13023-020-01460-2.
- *How the Management of Children With Congenital Central Hypoventilation Syndrome Has Changed Over Time: Two Decades of Experience From an Italian Center*, PMCID PMC8039127. Full bibliographic metadata/attribution is in the manifest.
- *Congenital Central Hypoventilation Syndrome: Optimizing Care with a Multidisciplinary Approach*, PMCID PMC8963195. Full bibliographic metadata/attribution is in the manifest.

Provider documentation: https://www.ncbi.nlm.nih.gov/research/bionlp/APIs/BioC-PMC/.
The fourth candidate PMC10235709 did not yield a usable response in the acquisition
attempt and is recorded as blocked, not counted as corpus coverage.

The included collection is deliberately small. It is not a systematic review,
complete CCHS bibliography or independently validated scientific knowledge base.
Correction/retraction impact review remains pending per source. A review's quoted
reference does not establish that the referenced primary study was acquired.

Prepared text preserves passage-local offsets. Bibliographies, metadata,
abbreviations and table/figure records are excluded from evidence indexing. Tables
and figure interpretation are outside the first parser's supported scope; an
answer cannot claim complete coverage of those results. Unknown study/population
context is retained as unknown. Original snapshots stay unchanged.

To refresh one snapshot, use the manifest's fixed official API URL, preserve the old
version in version control, inspect the new license/identity and update the manifest
hash deliberately. Re-ingest and rebuild question references when affected. Do not
silently mutate gold IDs or call a changed corpus the same experiment.
