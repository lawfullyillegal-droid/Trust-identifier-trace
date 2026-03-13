# GitHub Actions Artifacts Guide

## Overview

All scan workflows in this repository upload their outputs as GitHub Actions artifacts after each run. This ensures that scan results are always retrievable, even when commits back to the protected `main` branch are blocked by branch protection rules.

Artifacts are the **source of truth** for scan outputs. The `git push` steps are retained for convenience but are non-fatal — a workflow succeeds and produces an artifact whether or not the push to `main` succeeds.

---

## Artifact Naming Convention

All artifacts follow this naming pattern:

```
scan-<workflow-name>-<run_id>-<run_attempt>
```

| Token | Value | Example |
|---|---|---|
| `<workflow-name>` | `github.workflow` — the workflow's `name:` field | `Trust Scan Bot` |
| `<run_id>` | `github.run_id` — unique integer per run | `12345678` |
| `<run_attempt>` | `github.run_attempt` — attempt number (re-runs increment this) | `1` |

**Full example:** `scan-Trust Scan Bot-12345678-1`

---

## Workflow Artifacts

| Workflow file | Workflow name | Output path(s) uploaded |
|---|---|---|
| `trust_scan_bot.yml` | Trust Scan Bot | `output/scan_results.json` |
| `archive_scan.yml` | Archive Scan Results | `archive/` (entire directory) |
| `gleif-scan.yml` | Daily GLEIF Scan + Overlay Injection | `gleif_results.xml`, `trust_overlay.xml` |
| `identifier_connections_bot.yml` | Identifier Connections Bot | `output/identifier_connections.json` |
| `incrimination-nation.yml` | Incrimination Nation - Public Record Scraper | `public_records/` (entire directory) |
| `reddit_trace_bot.yml` | Reddit Trace Bot | `output/reddit_trace_results.json` |
| `syndicate_output.yml` | Syndicate Output Generator | `output/syndicate_dashboard_data.json` |

---

## Output Verification

Each workflow includes a **Verify** step immediately before the artifact upload. This step:

1. Checks that the expected output file or directory exists.
2. Fails the job with a clear error message if the output is missing.
3. Logs a ✅ confirmation when the output is present.

This prevents the `actions/upload-artifact` step from silently uploading empty artifacts and ensures that a green workflow run means the scan actually produced data.

---

## How to Download Artifacts

### From the GitHub Actions UI

1. Go to the **Actions** tab of the repository.
2. Click the workflow run you want to inspect.
3. Scroll to the **Artifacts** section at the bottom of the run summary page.
4. Click the artifact name (e.g., `scan-Trust Scan Bot-12345678-1`) to download a `.zip` file.
5. Unzip the file to access the scan output(s).

### Using the GitHub CLI

```bash
# List artifacts for a specific run
gh run view <run_id> --repo lawfullyillegal-droid/Trust-identifier-trace

# Download a specific artifact
gh run download <run_id> --name "scan-Trust Scan Bot-<run_id>-1" \
  --dir evidence/actions-artifacts/trust-scan-bot/<run_id>/
```

---

## Suggested Local Archival Path

When downloading artifacts for evidence preservation, use the following directory structure to keep outputs organized and traceable:

```
evidence/actions-artifacts/<workflow>/<run_id>/
```

### Examples

```
evidence/actions-artifacts/trust-scan-bot/12345678/scan_results.json
evidence/actions-artifacts/archive-scan/12345679/archive/scan_results_2026-03-13_12-00-00.json
evidence/actions-artifacts/gleif-scan/12345680/gleif_results.xml
evidence/actions-artifacts/gleif-scan/12345680/trust_overlay.xml
evidence/actions-artifacts/identifier-connections-bot/12345681/identifier_connections.json
evidence/actions-artifacts/incrimination-nation/12345682/public_records/records.json
evidence/actions-artifacts/reddit-trace-bot/12345683/reddit_trace_results.json
evidence/actions-artifacts/syndicate-output/12345684/syndicate_dashboard_data.json
```

---

## Artifact Retention

GitHub Actions artifacts are retained for **90 days** by default. This default can be changed in repository or organization settings, and may differ based on your GitHub plan. To preserve artifacts permanently:

- Download them promptly and store them using the archival path above.
- Attach key artifacts to a GitHub Release for permanent storage.
- Use the GitHub CLI (`gh run download`) to automate bulk downloads.

---

## Relationship to `git push`

The `git push` steps in each workflow are retained so that outputs can still land in the repository when branch protection allows it. However, they are **non-fatal**:

```yaml
git push || echo "Push skipped due to branch protection rules"
```

If a push is blocked, the workflow still succeeds and the artifact remains available for download. The artifact is therefore the authoritative, always-available copy of each run's output.
