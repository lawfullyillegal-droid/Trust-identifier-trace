# Testing Network Connectivity Enhancements in GitHub Actions

This document provides instructions for testing the network connectivity fixes in the actual GitHub Actions environment.

## Overview

The network enhancements have been implemented and tested locally in a sandboxed environment. To verify they work correctly in GitHub Actions, follow these testing steps.

## Prerequisites

- Access to the Trust-identifier-trace repository
- Permissions to run GitHub Actions workflows
- Understanding that GitHub Actions runners should have normal internet access

## Test Plan

### Phase 1: Network Diagnostics Workflow

**Purpose**: Verify basic network connectivity and DNS resolution in GitHub Actions

**Steps**:
1. Go to the repository Actions tab
2. Select "Network Diagnostics" workflow
3. Click "Run workflow" → "Run workflow" (main branch)
4. Wait for completion (should take ~1-2 minutes)

**Expected Results**:
- ✅ DNS resolution tests should PASS for all services
- ✅ HTTP connectivity tests should PASS for all services
- ✅ Python requests tests should PASS for all services

**If Tests Fail**:
- Review the workflow logs for specific error messages
- Check if GitHub is experiencing service issues: https://www.githubstatus.com
- Review the "Network Environment Info" step for configuration details

### Phase 2: Trust Scan Bot

**Purpose**: Verify the trust scan bot can connect to Reddit API and gather real data

**Steps**:
1. Go to the repository Actions tab
2. Select "Trust Scan Bot" workflow
3. Click "Run workflow" → "Run workflow"
4. Wait for completion

**Expected Results**:
- ✅ DNS configuration step should show "DNS resolution working correctly"
- ✅ Network connectivity test should show passes for Reddit and GLEIF
- ✅ Bot should gather real Reddit data (not mock data)
- ✅ `output/scan_results.json` should contain actual Reddit mentions

**What to Check**:
```bash
# Look for in the logs:
✅ DNS resolution working correctly
📡 Attempt 1/3: GET https://www.reddit.com/search.json...
✅ Request successful: Status 200

# NOT this (which indicates offline mode):
⚠️ Network error querying Reddit
🔄 Falling back to offline mode with mock data
```

### Phase 3: GLEIF Scan

**Purpose**: Verify GLEIF API connectivity and data gathering

**Steps**:
1. Go to the repository Actions tab
2. Select "Daily GLEIF Scan + Overlay Injection" workflow
3. Click "Run workflow" → "Run workflow"
4. Wait for completion

**Expected Results**:
- ✅ DNS configuration step should succeed
- ✅ Network connectivity test should pass for GLEIF
- ✅ Bot should fetch real GLEIF data
- ✅ Results should contain actual LEI records

**What to Check**:
```bash
# Look for in the logs:
🔍 Checking DNS resolution for api.gleif.org...
📡 Attempt 1/3: GET https://api.gleif.org/api/v1/lei-records...
✅ Request successful: Status 200
✅ Successfully fetched GLEIF data

# NOT this:
⚠️ Network error: DNS resolution failed
🔄 Running in offline mode with mock data...
```

### Phase 4: Reddit Trace Bot

**Purpose**: Verify comprehensive Reddit profiling functionality

**Steps**:
1. Go to the repository Actions tab
2. Select "Reddit Trace Bot" workflow
3. Click "Run workflow" → "Run workflow"
4. Wait for completion

**Expected Results**:
- ✅ Bot should use enhanced network utilities
- ✅ Should gather real Reddit data with risk profiles
- ✅ `output/reddit_trace_results.json` should contain actual mentions
- ✅ Risk summary should be based on real data

**What to Check**:
```bash
# Look for in the logs:
📡 Attempt 1/3: GET https://www.reddit.com/search.json...
✅ Request successful: Status 200
✅ Found X Reddit posts for [identifier]
🎯 Risk Summary: X HIGH, X MEDIUM, X LOW

# Should NOT show:
⚠️ Warning: X identifiers processed in offline mode
```

## Verification Checklist

After running all tests, verify:

- [ ] Network Diagnostics workflow shows all tests passing
- [ ] Trust Scan Bot connects to Reddit successfully
- [ ] GLEIF Scan connects to GLEIF API successfully
- [ ] Reddit Trace Bot gathers real data with risk profiles
- [ ] No "offline mode" or "mock data" messages in logs
- [ ] Output files contain real API data (not mock data)

## Troubleshooting Failed Tests

### If DNS Tests Fail in GitHub Actions

This is unexpected for standard GitHub runners. Possible causes:

1. **Temporary GitHub Service Issue**
   - Check https://www.githubstatus.com
   - Wait and retry

2. **Organization Network Policies**
   - Enterprise GitHub may have restrictions
   - Contact GitHub admin to allowlist:
     - api.gleif.org
     - www.reddit.com

3. **Self-Hosted Runner Issues**
   - Verify runner has internet access
   - Check runner network configuration

### If Bots Run in Offline Mode

Check the logs for specific error messages:

**DNS Resolution Failed**:
```
❌ DNS resolution failed for api.gleif.org
```
→ DNS configuration issue, see NETWORK_TROUBLESHOOTING.md

**Connection Timeout**:
```
⏱️ Timeout on attempt 3/3
```
→ Network firewall or proxy issue

**HTTP Error**:
```
❌ HTTP 429: Too Many Requests
```
→ Rate limiting (should auto-retry with backoff)

## Expected Performance

### With Network Access:
- Network Diagnostics: ~1-2 minutes
- Trust Scan Bot: ~2-3 minutes
- GLEIF Scan: ~2-4 minutes (depending on data size)
- Reddit Trace Bot: ~3-5 minutes

### Retry Behavior:
- Initial request: Immediate
- First retry: After 1.5 seconds
- Second retry: After 3 seconds
- Third retry: After 6 seconds

Total max time for single request with all retries: ~20 seconds

## Success Criteria

The network connectivity enhancements are working correctly if:

1. ✅ Workflows complete successfully (green checkmark)
2. ✅ Bots connect to real APIs (not offline mode)
3. ✅ Output contains actual data (not mock data)
4. ✅ Logs show successful HTTP requests
5. ✅ No DNS resolution errors in logs
6. ✅ Retry logic activates on transient failures (if any)

## Reporting Results

After testing, document:

1. **What worked**:
   - Which workflows succeeded
   - Which APIs were reached successfully
   - Sample log output showing success

2. **What needs improvement**:
   - Any remaining connectivity issues
   - Specific error messages
   - Environmental factors

3. **Recommendations**:
   - Configuration changes needed
   - Documentation updates
   - Further enhancements

## Next Steps After Successful Testing

1. Monitor workflow runs for consistent success
2. Review output files to ensure data quality
3. Adjust retry/timeout settings if needed
4. Update documentation based on findings
5. Consider adding monitoring/alerting

## Support

For issues during testing:
- Review workflow logs carefully
- Check [NETWORK_TROUBLESHOOTING.md](NETWORK_TROUBLESHOOTING.md)
- Run `python network_utils.py` locally for comparison
- Document specific errors for support requests

---

**Note**: These tests are designed to work in standard GitHub Actions runners. If you're using self-hosted runners or enterprise GitHub with network restrictions, you may need to work with your network administrator to enable access to the required APIs.
