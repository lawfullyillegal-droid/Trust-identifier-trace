# Incrimination Nation — Operational Runbook

## Current verified state

The prior scheduled “Public Record Scraper” did not retrieve records; it wrote `sample_data` with a timestamp and auto-committed it. The old homepage displayed static counts with no substantiation. The corrected workflow **validates**, but does not scrape, issue notices, file complaints, or promise monetary recovery.

## Working pipeline

1. Keep originals and nonpublic evidence outside all public Git repositories, preferably encrypted and access-controlled. Preserve untouched originals and a private chain-of-custody ledger.
2. Enter **only approved public, nonsensitive** records in the committed `public_records/intake.json` using the schema `sources`, `claims`, `links`. Every entry there must have `public: true`; private/unpublished entries and `local_path` are forbidden in that tracked file. Use a separate, untracked manifest under `private/` for mixed or private records. The `public` flag never hides input data already committed to GitHub.
3. For each public `source`: `id`, `title`, official HTTPS `url`, `public: true`; optionally `sha256` (64 lowercase hex characters). The optional `local_path` is **only for untracked private manifests**. Never commit local source files or a manifest containing private paths. Local hashing proves byte identity, not authenticity or the allegation.
4. For each public `claim`: `id`, `statement`, `status` (`allegation`, `documented`, `disputed`, `withdrawn`), `source_ids`, `public: true`. `documented` requires a source. Classifying an item as documented is a research status, not a court finding.
5. For each public `link`: `from` and `to` claim IDs, `relationship`, one or more `source_ids`, `public: true`. Connections require explicit sources; similar names are not enough.
6. Run the commands below, review the JSON diff and privacy exposure, then commit the output. The scheduled workflow never auto-commits data.

```sh
python -m unittest discover -s tests -v
python scripts/incrimination_nation.py --input public_records/intake.json --output public_records/records.json
git diff -- public_records/records.json
git status --short
```

## Case tracks and highest-impact missing records

- **Mohave/Kingman court:** certified docket, minute entries and any ruling on pending motions; link every legal claim to the exact order or transcript. Defense deadlines take priority over publicity.
- **ADOT/MVD / FARE-TTEAP:** certified driving record; each suspension identifier and effective date; notice and hearing history; holds/collections ledger; source-level contradiction table.
- **Consumer reporting:** original disclosures, exact inaccurate fields, dated dispute letters, investigative responses, publication/use, and provable harm. A database appearance by itself does not establish an FCRA violation.
- **Ventura / Aztec:** primary arrest/contract/UCC documents and chronology; do not infer a coordinated scheme from common names or contract totals.
- **Child support/family:** keep confidential records and children's details out of the public index.

## Safety and integrity

- Repository is **public**. Existing Git history may expose sensitive identifiers; deleting a file from today's tree does **not** erase previous commits. Audit all cloned copies and history before any destructive rewrite.
- GitHub Pages must never publish `output/`, `archive/`, `overlays/`, `identifiers.json`, case exhibits, or any private evidence directory.
- The older legal notice is a party-authored allegation document, not an adjudicated set of findings, proof that formal notice was served, or an automatic settlement demand.
- Do not automate sending accusations, initiating cases, threatening individuals, or publishing disputed personal data.
- No refunds, damages, settlement, or revenue are guaranteed; record actual damages with dates, contemporaneous proof, and legal causation before making claims.
