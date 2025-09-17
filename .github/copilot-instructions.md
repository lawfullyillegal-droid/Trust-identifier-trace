# Trust Identifier Trace Copilot Instructions

Always follow these instructions first and fallback to additional search and context gathering only if the information here is incomplete or found to be in error.

## Working Effectively

### Environment Setup
- Bootstrap the repository:
  - `pip install -r requirements.txt` -- takes 1-2 seconds in most environments
  - Dependencies: Python 3.11+ with `pyyaml` and `requests` packages
- All Python scripts import successfully but most fail during execution due to network dependencies

### Core Scripts and Execution Times
- `python3 find_failing_codes.py` -- takes 1-2 seconds. NEVER CANCEL. Always runs successfully and provides comprehensive analysis of script functionality
- `python3 gleif_trace.py` -- takes <1 second. NEVER CANCEL. Runs successfully but network calls fail gracefully with error logging
- `python3 trust_scan_bot.py` -- FAILS due to Reddit API network dependency. Will fail with NameResolutionError
- `python3 gleif_echo.py` -- FAILS immediately on import due to GLEIF API network dependency  
- `python3 gleif_alias_scan.py` -- FAILS immediately on import due to GLEIF API network dependency

### Network Dependency Status
**CRITICAL**: Most scripts require external network access and will FAIL in sandboxed environments:
- Scripts that FAIL: `gleif_echo.py`, `gleif_alias_scan.py`, `trust_scan_bot.py` 
- Scripts that work offline: `find_failing_codes.py`, `gleif_trace.py` (with graceful error handling), `reddit_trace.py` (import only)
- All network failures manifest as `NameResolutionError: Failed to resolve [hostname]`

### Testing and Validation
- Run the analysis script to verify environment: `python3 find_failing_codes.py`
- Start local server for dashboard testing: `python3 -m http.server 8000 --bind 127.0.0.1`
- Access dashboards at: `http://127.0.0.1:8000/dashboard.html` and `http://127.0.0.1:8000/syndicate_dashboard.html`
- **VALIDATION SCENARIOS**: 
  - Verify `find_failing_codes.py` completes successfully and reports analysis
  - Test dashboard loads and displays scan results table with 9 verified identifiers
  - Verify overlay files generation in `overlays/` directory
  - Check `output/scan_results.json` contains properly formatted identifier data

### Dashboard Functionality
- **Trust Scan Dashboard**: Fully functional with search, data table, and overlay links. Uses D3.js (may fail to load in restricted environments)
- **Syndicate Dashboard**: Shows title only; requires archive files that may not exist in fresh clones
- Dashboards read from `output/scan_results.json` and display identifier status, sources, and overlay links

## Key Repository Structure

### Core Python Scripts
- `trust_scan_bot.py`: Main scan bot for identifier processing (network-dependent)
- `gleif_trace.py`: GLEIF API scanner with graceful error handling
- `reddit_trace.py`: Reddit API query functions
- `find_failing_codes.py`: Repository health analysis tool (always works)
- `gleif_echo.py`, `gleif_alias_scan.py`: GLEIF challenge scans (network-dependent)

### Data and Configuration
- `identifiers.json`: Core identifier definitions (9 identifiers)
- `requirements.txt`: Python dependencies (pyyaml, requests)
- `output/`: Scan results and log files
- `overlays/`: Generated YAML overlay files for identifiers
- `.github/workflows/`: GitHub Actions for automated scanning

### Dashboards and UI
- `dashboard.html`: Interactive trust scan results viewer
- `syndicate_dashboard.html`: Multi-run aggregation dashboard
- `index.html`: Repository landing page

## Common Tasks

### Running Analysis
```bash
# Always start with this - it works in all environments
python3 find_failing_codes.py

# Expected output: Analysis of 5 Python files with ~40% success rate
# Runtime: 1-2 seconds
```

### Testing Dashboards
```bash
# Start local server (NEVER CANCEL - runs indefinitely)
python3 -m http.server 8000 --bind 127.0.0.1 &

# Test dashboard access
curl -I http://127.0.0.1:8000/dashboard.html
# Expected: HTTP 200 OK response

# Stop server when done
pkill -f "python3 -m http.server"
```

### Understanding Network Failures
All network-dependent scripts will fail with connection errors like:
```
NameResolutionError: Failed to resolve 'api.gleif.org'
HTTPSConnectionPool(...): Max retries exceeded
```
This is expected behavior in sandboxed environments. Do not attempt to fix network connectivity.

## GitHub Actions Integration
- Workflows exist in `.github/workflows/` for automated scanning
- `trust_scan_bot.yml`: Runs trust scan bot with results commit
- `gleif-scan.yml`: Daily GLEIF scanning with overlay injection
- Workflows assume network connectivity and will fail in restricted environments

## Output and Artifacts
- `output/scan_results.json`: Formatted scan results for dashboard consumption
- `output/scan_log.txt`: Detailed execution logs with timestamps
- `failing_codes_report.json`: Comprehensive analysis of script functionality
- Generated overlay files in `overlays/` directory

## Working with Identifiers
The repository tracks 9 core identifiers:
- EIN-92-6319308, SSN-602-05-7209, IRS-TRACK-108541264370
- CSE-CASE-200000002519088, ADOT-CUST-16088582
- Address, Entity Name, Birth Registry, Property Record numbers
All identifiers have corresponding overlay files and dashboard entries.

## Timeout and Performance Expectations
- **Dependency installation**: 1-2 seconds
- **Analysis scripts**: 1-2 seconds  
- **Dashboard server startup**: Immediate
- **Network-dependent scripts**: Fail immediately with connection errors
- **NEVER CANCEL** any long-running processes - if something appears to hang, wait at least 60 seconds

## Troubleshooting
- If scripts fail with network errors: This is expected in sandboxed environments
- If dashboards don't load: Check that HTTP server is running on port 8000
- If analysis shows low success rate: This is normal due to network dependencies
- For any unexpected behavior: Run `python3 find_failing_codes.py` for current status

## When Making Changes
- Always run `python3 find_failing_codes.py` after modifications to verify functionality
- Test dashboard functionality via local HTTP server
- Verify overlay file generation in the `overlays/` directory
- Check that `output/scan_results.json` remains properly formatted
- Understand that network-dependent features cannot be fully tested in restricted environments