# Failing Codes Report for Trust-identifier-trace Repository

## Executive Summary

This report identifies all failing codes in the Trust-identifier-trace repository as requested. The analysis was conducted on 2025-09-13 and includes systematic testing of all Python scripts, configuration files, and runtime behavior.

## Failing Python Scripts

### 1. gleif_echo.py - CRITICAL FAILURE
- **Type**: Import Error / Network Connectivity Failure
- **Root Cause**: Cannot resolve 'api.gleif.org' hostname
- **Error**: `NameResolutionError: Failed to resolve 'api.gleif.org'`
- **Impact**: Script fails at module import level due to immediate network call
- **Status**: FAILING

### 2. gleif_alias_scan.py - CRITICAL FAILURE  
- **Type**: Import Error / Network Connectivity Failure
- **Root Cause**: Cannot resolve 'api.gleif.org' hostname
- **Error**: `NameResolutionError: Failed to resolve 'api.gleif.org'`
- **Impact**: Script fails at module import level due to immediate network call
- **Status**: FAILING (Fixed KeyError issue but still fails on network)

### 3. trust_scan_bot.py - RUNTIME FAILURE
- **Type**: Runtime Error / Network Connectivity Failure
- **Root Cause**: Cannot resolve 'www.reddit.com' hostname
- **Error**: `NameResolutionError: Failed to resolve 'www.reddit.com'`
- **Impact**: Script imports successfully but fails during execution
- **Status**: FAILING

## Working Scripts (with Internal Failures)

### 4. gleif_trace.py - PARTIAL FAILURE
- **Type**: Runtime Success but Functional Failure
- **Root Cause**: Network calls fail but script handles errors gracefully
- **Error**: Multiple connection errors for each identifier scan
- **Impact**: Script runs to completion but all scans fail
- **Status**: TECHNICALLY SUCCESSFUL but FUNCTIONALLY FAILING

### 5. reddit_trace.py - IMPORT SUCCESS
- **Type**: Import Success
- **Status**: SUCCESSFUL (but would fail when actually used)

## Additional Failing Components Found

### 6. Historical Scan Failures
- **File**: `output/scan_log.txt`
- **Content**: Contains numerous connection errors for identifier scans
- **Pattern**: All 14 identifiers fail with NameResolutionError to 'api.gleif.org'

### 7. Configuration Issues (Fixed)
- **File**: `identifiers.yaml`
- **Issue**: Missing 'trust_aliases' key required by gleif_alias_scan.py
- **Status**: FIXED - Added trust_aliases section

## Network Dependency Analysis

All failing codes share a common issue: **network connectivity dependencies** in a sandboxed environment that blocks external connections.

### Failed External Services:
1. `api.gleif.org` - GLEIF API for legal entity identification
2. `www.reddit.com` - Reddit API for content scanning
3. Various other services referenced in logs

## Summary Statistics

- **Total Python files tested**: 5
- **Critical failures**: 3 files (60%)
- **Functional failures**: 1 file (20%) 
- **Successful imports**: 2 files (40%)
- **Overall success rate**: 40% (but functionally 20%)

## Root Cause Analysis

The primary failure mode is **network connectivity blocking** in the execution environment. All scripts that make immediate network calls during import or early execution fail with DNS resolution errors.

### Failure Pattern:
1. Script attempts to connect to external API
2. DNS resolution fails with "No address associated with hostname"
3. urllib3/requests raises NameResolutionError
4. Script terminates with ConnectionError

## Recommended Actions

1. **Immediate**: Add offline/mock modes to all network-dependent scripts
2. **Short-term**: Implement proper error handling for network failures
3. **Long-term**: Add environment detection and graceful degradation

---

*Analysis completed: 2025-09-13*  
*Tool used: find_failing_codes.py*  
*Environment: Sandboxed with network restrictions*