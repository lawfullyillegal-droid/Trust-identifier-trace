# Network Connectivity Troubleshooting Guide

## Overview
This guide helps diagnose and resolve network connectivity issues that prevent the Trust-identifier-trace bots from reaching external APIs (Reddit, GLEIF).

## Quick Diagnostic

Run the network diagnostics workflow to test connectivity:
```bash
# Trigger via GitHub Actions UI: 
# Actions → Network Diagnostics → Run workflow
```

Or run locally:
```bash
python network_utils.py
```

## Common Issues and Solutions

### 1. DNS Resolution Failures

**Symptoms:**
- Error: `NameResolutionError: Failed to resolve [hostname]`
- Error: `DNS resolution failed for [hostname]`

**Causes:**
- DNS server unavailable or misconfigured
- Network firewall blocking DNS queries
- Sandboxed environment restrictions

**Solutions:**

#### A. Verify DNS Configuration
```bash
# Check DNS resolver
cat /etc/resolv.conf

# Test DNS lookup
nslookup api.gleif.org
dig www.reddit.com
```

#### B. Alternative DNS Servers
If the default DNS is failing, configure alternative DNS:

Add to workflow before bot execution:
```yaml
- name: Configure DNS
  run: |
    echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
    echo "nameserver 1.1.1.1" | sudo tee -a /etc/resolv.conf
```

#### C. Use IP Addresses (Not Recommended)
If DNS is completely blocked, you can use IP addresses, but this is fragile:
```python
# This is a workaround, not a permanent solution
GLEIF_IP = "X.X.X.X"  # Lookup current IP first
```

### 2. Network Firewall Blocking Outbound Connections

**Symptoms:**
- DNS works but HTTP requests timeout
- Connection refused errors
- Requests hang indefinitely

**Solutions:**

#### A. Check Firewall Rules
```bash
# Test connectivity with curl
curl -v https://api.gleif.org/api/v1/lei-records?page[size]=1
curl -v https://www.reddit.com/robots.txt

# Check if specific ports are blocked
nc -zv api.gleif.org 443
nc -zv www.reddit.com 443
```

#### B. Use Proxy (if provided)
If your environment requires a proxy:

Add to workflow:
```yaml
- name: Configure Proxy
  run: |
    export HTTP_PROXY="http://proxy.example.com:8080"
    export HTTPS_PROXY="http://proxy.example.com:8080"
  env:
    HTTP_PROXY: ${{ secrets.HTTP_PROXY }}
    HTTPS_PROXY: ${{ secrets.HTTPS_PROXY }}
```

Update Python code to use proxy:
```python
import os
proxies = {
    'http': os.getenv('HTTP_PROXY'),
    'https': os.getenv('HTTPS_PROXY'),
}
response = requests.get(url, proxies=proxies)
```

### 3. GitHub Actions Runner Network Restrictions

**Symptoms:**
- Works locally but fails in GitHub Actions
- All external APIs fail simultaneously

**Solutions:**

#### A. Verify Runner Type
Ensure you're using the correct runner:

```yaml
jobs:
  bot-job:
    runs-on: ubuntu-latest  # Should have internet access
```

Self-hosted runners may have restricted network access.

#### B. Check Organization/Enterprise Settings
- GitHub Enterprise may have network restrictions
- Contact your GitHub admin to allowlist:
  - `api.gleif.org`
  - `www.reddit.com`
  - Any other required domains

#### C. Use GitHub's IP Allow List
Add trusted external services to IP allow list:
https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions

### 4. Rate Limiting

**Symptoms:**
- First few requests succeed, then fail
- HTTP 429 errors
- Temporary connection failures

**Solutions:**

The bots now include:
- Exponential backoff retry logic (automatically applied)
- Configurable retry attempts (default: 3)
- Request throttling

Adjust in code if needed:
```python
from network_utils import make_request_with_retry

response = make_request_with_retry(
    url=api_url,
    max_retries=5,      # Increase retries
    timeout=30,         # Increase timeout
    backoff_factor=2.0  # Slower retry backoff
)
```

### 5. SSL/TLS Certificate Issues

**Symptoms:**
- SSL certificate verification failed
- CERTIFICATE_VERIFY_FAILED errors

**Solutions:**

#### A. Update CA Certificates
```yaml
- name: Update CA certificates
  run: |
    sudo apt-get update
    sudo apt-get install -y ca-certificates
    sudo update-ca-certificates
```

#### B. Temporary Workaround (NOT RECOMMENDED FOR PRODUCTION)
```python
# Only for testing in development
response = requests.get(url, verify=False)
```

## Testing Network Connectivity

### Run Full Diagnostic Suite

```bash
# 1. Test DNS
python -c "import socket; print(socket.gethostbyname('api.gleif.org'))"

# 2. Test HTTP connectivity
python -c "import requests; r=requests.get('https://api.gleif.org/api/v1/lei-records?page[size]=1', timeout=5); print(r.status_code)"

# 3. Run network utils test
python network_utils.py

# 4. Test individual bots
python gleif_echo.py
python reddit_trace.py
python trust_scan_bot.py
```

### Monitor Workflow Runs

Check workflow logs for:
- DNS resolution test results
- HTTP connectivity test results  
- Bot execution output
- Network error messages

## Escalation Path

If network issues persist after trying all solutions:

1. **Document the failure:**
   - Run `network_utils.py` and save output
   - Capture workflow logs
   - Note exact error messages

2. **Check GitHub Status:**
   - Visit https://www.githubstatus.com
   - Check for Actions service disruptions

3. **Contact Support:**
   - GitHub Enterprise: Contact admin
   - GitHub.com: Check GitHub Community
   - API providers: Verify service status
     - GLEIF: https://www.gleif.org
     - Reddit: https://www.redditstatus.com

## Enhanced Features

The bots now include:

### Automatic Retry Logic
- 3 retry attempts by default
- Exponential backoff between retries
- Configurable timeout and backoff parameters

### DNS Pre-Check
- Validates DNS resolution before HTTP requests
- Provides clear error messages for DNS failures
- Fails fast when DNS is unavailable

### Comprehensive Error Reporting
- Detailed error messages with troubleshooting hints
- Distinction between DNS, connection, and HTTP errors
- Offline mode with mock data when network unavailable

### Network Diagnostics
- Pre-flight connectivity checks in workflows
- Detailed network environment information
- Service-specific connectivity tests

## Configuration Options

### Environment Variables

You can set these in GitHub Actions secrets or environment:

```yaml
env:
  # Network timeouts (seconds)
  NETWORK_TIMEOUT: "30"
  NETWORK_MAX_RETRIES: "5"
  NETWORK_BACKOFF_FACTOR: "2.0"
  
  # Proxy configuration (if needed)
  HTTP_PROXY: ${{ secrets.HTTP_PROXY }}
  HTTPS_PROXY: ${{ secrets.HTTPS_PROXY }}
  
  # DNS servers (if needed)
  DNS_SERVER_1: "8.8.8.8"
  DNS_SERVER_2: "1.1.1.1"
```

## Monitoring and Alerts

Set up monitoring for:
- Workflow success/failure rates
- Network error frequencies
- API response times
- Offline mode activations

Consider adding notification steps to workflows:
```yaml
- name: Notify on failure
  if: failure()
  run: |
    echo "Network connectivity check failed"
    # Add notification logic (email, Slack, etc.)
```

## Additional Resources

- [GitHub Actions Network Troubleshooting](https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/about-self-hosted-runners#network-requirements)
- [GLEIF API Documentation](https://www.gleif.org/en/lei-data/gleif-api)
- [Reddit API Guidelines](https://www.reddit.com/dev/api/)
- [Python Requests Library](https://requests.readthedocs.io/)
