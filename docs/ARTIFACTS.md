# Artifacts Documentation

This document describes how artifacts are handled in the GitHub Actions workflows of the Trust Identifier Trace project.

## Artifact Uploads

All scan workflows are configured to upload artifacts, ensuring outputs are persisted reliably, independent of protected branch pushes. This includes the following scan workflows:

- **archive_scan.yml**: Handles archiving of scan results.
- **gleif-scan.yml**: Scans GLEIF records and generates artifacts.
- **identifier_connections_bot.yml**: Manages connections for identifiers and uploads related artifacts.
- **incrimination-nation.yml**: Runs scans and persists results.
- **reddit_trace_bot.yml**: Traces Reddit content and stores relevant outputs.
- **syndicate_output.yml**: Outputs from syndicate scans are preserved.
- **trust_scan_bot.yml**: Conducts trust scans and artifacts are uploaded.

### Configurations
Artifacts are uploaded using the `actions/upload-artifact@v2` action in each workflow YAML file. The specific configurations may vary depending on the output needs of each scan process. For detailed configurations, refer to the individual workflow files.