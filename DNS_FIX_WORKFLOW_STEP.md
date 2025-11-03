# DNS Configuration Step for GitHub Actions Workflows

If you're experiencing DNS resolution failures in GitHub Actions, you can add this step to your workflows to attempt DNS configuration fixes.

## Usage

Add this step **before** running the bots in your workflow:

```yaml
- name: Configure DNS (if needed)
  run: |
    # Test if DNS is working
    if ! nslookup api.gleif.org > /dev/null 2>&1; then
      echo "⚠️ DNS resolution failing, attempting to configure alternative DNS..."
      
      # Try to configure Google DNS
      echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf > /dev/null
      echo "nameserver 8.8.4.4" | sudo tee -a /etc/resolv.conf > /dev/null
      echo "nameserver 1.1.1.1" | sudo tee -a /etc/resolv.conf > /dev/null
      
      # Test again
      if nslookup api.gleif.org > /dev/null 2>&1; then
        echo "✅ DNS resolution fixed with alternative DNS servers"
      else
        echo "⚠️ DNS still failing - network may be restricted"
        echo "Bots will run in offline mode with mock data"
      fi
    else
      echo "✅ DNS resolution working correctly"
    fi
```

## Full Example Workflow

```yaml
name: Trust Scan Bot with DNS Auto-Fix

on:
  workflow_dispatch:

permissions:
  contents: write

jobs:
  trust-scan:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Configure DNS (if needed)
        run: |
          # Test if DNS is working
          if ! nslookup api.gleif.org > /dev/null 2>&1; then
            echo "⚠️ DNS resolution failing, attempting to configure alternative DNS..."
            
            # Try to configure Google DNS
            echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf > /dev/null
            echo "nameserver 8.8.4.4" | sudo tee -a /etc/resolv.conf > /dev/null
            echo "nameserver 1.1.1.1" | sudo tee -a /etc/resolv.conf > /dev/null
            
            # Test again
            if nslookup api.gleif.org > /dev/null 2>&1; then
              echo "✅ DNS resolution fixed with alternative DNS servers"
            else
              echo "⚠️ DNS still failing - network may be restricted"
              echo "Bots will run in offline mode with mock data"
            fi
          else
            echo "✅ DNS resolution working correctly"
          fi

      - name: Test network connectivity
        run: python network_utils.py || echo "Network tests completed with some failures"

      - name: Run Trust Scan Bot
        run: python trust_scan_bot.py

      - name: Commit results
        run: |
          git config user.name "Trust Scan Bot"
          git config user.email "bot@trust.local"
          git add output/scan_results.json
          git commit -m "Auto-generate scan results" || echo "No changes"
          git push
```

## Alternative: Use DNS Helper Script

You can also use the `dns_config_helper.py` script:

```yaml
- name: Diagnose and fix DNS
  run: |
    python dns_config_helper.py || echo "DNS diagnostics completed"
```

## When to Use This

Use this DNS configuration step when:

1. **GitHub Actions workflows are failing** with DNS resolution errors
2. **Self-hosted runners** have restricted network access
3. **Enterprise GitHub** instances with custom network policies
4. **Testing shows DNS failures** in the workflow logs

## When NOT to Use This

Don't add this step if:

1. **Workflows are working fine** - no need to fix what isn't broken
2. **Running on standard GitHub-hosted runners** - they should have working DNS by default
3. **Organization policy prohibits DNS changes** - consult your admin first

## Troubleshooting

If the DNS configuration step doesn't help:

1. The issue is likely a **network firewall**, not DNS
2. Check if your organization blocks outbound connections
3. Verify port 443 (HTTPS) is not blocked
4. See [NETWORK_TROUBLESHOOTING.md](NETWORK_TROUBLESHOOTING.md) for more options

## Security Note

This step requires `sudo` to modify `/etc/resolv.conf`. This is safe in GitHub Actions runners (which are ephemeral), but should not be used carelessly in persistent environments.

## Expected Behavior

### Success Case:
```
✅ DNS resolution working correctly
```
or
```
⚠️ DNS resolution failing, attempting to configure alternative DNS...
✅ DNS resolution fixed with alternative DNS servers
```

### Restricted Environment:
```
⚠️ DNS resolution failing, attempting to configure alternative DNS...
⚠️ DNS still failing - network may be restricted
Bots will run in offline mode with mock data
```

In the restricted environment case, the bots will gracefully fall back to offline mode with mock data, and the workflow will complete successfully (not fail).
