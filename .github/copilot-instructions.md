# GitHub Copilot Instructions for Trust-identifier-trace Repository

This file provides comprehensive instructions for GitHub Copilot coding agents working in the Trust-identifier-trace repository.

## Repository Overview

Trust-identifier-trace is a comprehensive trust identifier scanning and analysis system that:
- Monitors trust-related identifiers across multiple platforms (GLEIF, Reddit, etc.)
- Provides automated workflows for scanning and archiving results
- Features interactive dashboards for data visualization
- Handles network connectivity issues gracefully with offline modes

## Environment Setup

### Dependencies Installation
```bash
# Install required Python packages
pip install requests pyyaml

# Expected completion time: 1-2 seconds
# NEVER CANCEL - this is a quick operation
```

### Repository Analysis
```bash
# Analyze repository status and failing codes
python3 find_failing_codes.py

# Expected output: Success rate: 100.0% ✅
# Expected completion time: 1-2 seconds
# This validates all Python scripts are working correctly
```

## Script Execution Guide

### Working Scripts (Offline Compatible)
1. **find_failing_codes.py** - Repository analysis tool
   - Always works: ✅ Fully functional
   - Expected result: 100% success rate report

2. **gleif_trace.py** - GLEIF identifier scanning
   - Works offline: ✅ Graceful error handling
   - Expected result: Creates output/scan_log.txt with scan results

3. **trust_scan_bot.py** - Trust identifier scanning bot
   - Works offline: ✅ Uses mock Reddit data when network unavailable
   - Expected result: Creates output/scan_results.json with identifier analysis

4. **reddit_trace.py** - Reddit content analysis
   - Works offline: ✅ Returns mock data when Reddit API unavailable
   - Expected result: Returns analysis results or fallback data

5. **gleif_echo.py** - GLEIF API test tool
   - Works offline: ✅ Creates gleif_echo.xml with sample data
   - Expected result: XML file with GLEIF entity data (real or mock)

6. **gleif_alias_scan.py** - GLEIF alias scanning
   - Works offline: ✅ Processes with sample data when API unavailable
   - Expected result: Creates gleif_results.xml with alias matching results

### Network-Dependent Behavior
Most scripts require external network access to function fully but will not fail when network is unavailable:

- **Expected Failure Pattern**: `NameResolutionError: Failed to resolve [hostname]`
- **Graceful Degradation**: Scripts continue with mock/sample data
- **No Script Crashes**: All scripts complete successfully even when APIs are unreachable

## Dashboard Access

### Trust Scan Dashboard
```bash
# Start local HTTP server for dashboard access
python3 -m http.server 8000

# Access at: http://localhost:8000/dashboard.html
# Features: Interactive identifier search, visual trace mapping, real-time data
# Expected data: 9 verified identifiers with Reddit analysis
```

### Syndicate Dashboard
```bash
# Access at: http://localhost:8000/syndicate_dashboard.html
# Features: Multi-run aggregation, status summaries, error tracking
# Expected data: Combined results from multiple scan runs
```

### Learning Analytics Dashboard
```bash
# Access at: http://localhost:8000/learning_analytics.html
# Features: GitHub repository metrics, development analytics, contributor stats
# Expected data: September 2025 development metrics and insights
```

## Validation Scenarios

### Complete System Test
```bash
# 1. Run repository analysis (expected: 100% success rate)
python3 find_failing_codes.py

# 2. Execute main scanning workflow (expected: creates JSON output)
python3 trust_scan_bot.py

# 3. Verify output files exist
ls -la output/scan_results.json output/scan_log.txt

# 4. Test dashboard functionality
python3 -m http.server 8000 &
# Navigate to http://localhost:8000/dashboard.html
# Expected: Interactive dashboard with 9 identifiers displayed
```

### Offline Mode Validation
```bash
# All scripts should complete successfully even without network access
python3 gleif_echo.py        # Creates gleif_echo.xml
python3 gleif_alias_scan.py  # Creates gleif_results.xml
python3 trust_scan_bot.py    # Creates scan_results.json
```

## File Structure Guide

### Core Scripts
- `find_failing_codes.py` - Repository health analysis
- `trust_scan_bot.py` - Main trust scanning workflow
- `gleif_*.py` - GLEIF API integration scripts
- `reddit_trace.py` - Reddit content analysis
- `storm_breaker.py` - Advanced identifier analysis tool

### Configuration Files
- `identifiers.json` - Main identifier list (JSON format)
- `identifiers.yaml` - Trust aliases and ADOT numbers (YAML format)
- `requirements.txt` - Python dependencies

### Output Directories
- `output/` - Current scan results and logs
- `archive/` - Timestamped historical results
- `overlays/` - Cryptographic overlay files

### Web Interface
- `dashboard.html` - Main trust scan dashboard
- `syndicate_dashboard.html` - Multi-run aggregation dashboard
- `learning_analytics.html` - GitHub analytics dashboard
- `index.html` - Landing page with navigation

### Automation
- `.github/workflows/` - GitHub Actions automation workflows
- `bots/` - Automated bot scripts

## Troubleshooting

### Common Issues and Solutions

1. **Network Connectivity Errors**
   - Expected: Scripts handle gracefully with mock data
   - Action: No action needed - this is expected behavior in sandboxed environments

2. **Missing Dependencies**
   ```bash
   pip install requests pyyaml
   ```

3. **Output Directory Missing**
   ```bash
   mkdir -p output archive overlays
   ```

4. **Permission Issues**
   ```bash
   chmod +x *.py
   ```

### Expected Error Patterns
- `NameResolutionError: Failed to resolve 'api.gleif.org'` - Normal in restricted environments
- `NameResolutionError: Failed to resolve 'www.reddit.com'` - Normal in restricted environments
- These errors are handled gracefully and should not cause script failures

## Performance Expectations

### Measured Execution Times
- Repository analysis: 1-2 seconds
- Trust scan execution: 2-3 seconds
- GLEIF operations: 1-2 seconds
- Dashboard server startup: Immediate

### Success Metrics
- Repository analysis should show 100% success rate
- All scripts should complete without exceptions
- Output files should be generated consistently
- Dashboards should load with interactive features

## Development Guidelines

### Code Style
- Use proper error handling for all network operations
- Implement graceful degradation for offline scenarios
- Include informative log messages and user feedback
- Maintain consistent timestamp formatting (UTC)

### Testing Approach
- Always test offline functionality
- Verify output file generation
- Validate dashboard interactions
- Check workflow automation

### Data Handling
- Use `datetime.now(timezone.utc)` instead of deprecated `datetime.utcnow()`
- Handle missing files gracefully with try-catch blocks
- Provide meaningful fallback data for offline modes
- Ensure all JSON output is valid and well-structured

## GitHub Actions Integration

The repository includes automated workflows for:
- Daily trust scanning (`trust_scan_bot.yml`)
- GLEIF data synchronization (`gleif-scan.yml`)
- Result archiving (`archive_scan.yml`)
- Reddit trace analysis (`reddit_trace_bot.yml`)
- Syndicate output generation (`syndicate_output.yml`)
- GitHub Pages deployment (`deploy-pages.yml`)

Expected workflow behavior:
- All workflows should complete successfully
- Network failures are handled gracefully
- Results are automatically committed and archived
- Dashboards are updated with latest data

## Pre-Commit Validation

**CRITICAL:** Before committing any changes, you MUST follow the pre-commit validation process:

📋 **See [PRE_COMMIT_INSTRUCTIONS.md](.github/PRE_COMMIT_INSTRUCTIONS.md) for complete validation steps**

### Quick Pre-Commit Checklist:
1. Run `python3 find_failing_codes.py` - Must show 100% success rate ✅
2. Review `git status` and `git diff` - Ensure only intended files are staged
3. Verify no generated artifacts are being committed (check .gitignore)
4. Test any modified scripts execute successfully
5. Check for hardcoded secrets or credentials
6. Prepare meaningful commit message

**Never skip validation** - it takes less than 30 seconds and ensures code quality.

## Important Notes

- **NEVER CANCEL** operations that complete within expected timeframes
- Most scripts are designed to work offline with mock data
- Dashboard functionality is fully operational with existing data
- Network connectivity issues are expected and handled gracefully
- All output files are generated consistently regardless of network status
- **Always validate before committing** - see PRE_COMMIT_INSTRUCTIONS.md

This repository is designed to be robust and functional in any environment, including sandboxed or network-restricted scenarios.