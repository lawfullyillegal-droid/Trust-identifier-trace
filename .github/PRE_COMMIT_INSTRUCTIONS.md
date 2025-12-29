# Pre-Commit Validation Instructions for GitHub Copilot

This file provides specific instructions for GitHub Copilot agents to validate code before committing changes to the Trust-identifier-trace repository.

## CRITICAL: Always Run Before Committing

**MANDATORY VALIDATION STEP:** Before using `report_progress` or making any commit, you MUST run the repository validation script to ensure all code is functional.

```bash
python3 find_failing_codes.py
```

**Expected Result:** 
- Success rate: 100.0% ✅
- All Python scripts should execute without errors
- Execution time: 1-2 seconds

**If validation fails:**
1. Review the error output in `failing_codes_log.txt`
2. Fix the issues in the failing scripts
3. Re-run validation until 100% success rate is achieved
4. Only then proceed with committing

## Pre-Commit Validation Checklist

Before committing any changes, complete ALL of the following steps:

### 1. Code Validation
```bash
# Run the comprehensive code validation script
python3 find_failing_codes.py

# Verify 100% success rate in output
# Check failing_codes_report.json for any issues
```

### 2. Dependency Check
```bash
# Ensure all required dependencies are listed
cat requirements.txt

# Verify dependencies are installed
pip list | grep -E "(requests|pyyaml)"
```

### 3. Syntax and Import Validation
```bash
# For any modified Python files, verify syntax
python3 -m py_compile <modified_file.py>

# Test imports don't fail
python3 -c "import <module_name>"
```

### 4. Runtime Testing
For any modified Python scripts, test execution:
```bash
# Run the modified script to ensure it executes without errors
python3 <modified_script.py>

# Expected: Script should complete successfully
# Network errors are acceptable if handled gracefully
```

### 5. Output Files Check
```bash
# Review what files will be committed
git status
git diff --stat

# Ensure you're not committing:
# - Temporary files (*.tmp, *.temp)
# - Build artifacts (dist/, build/, *.egg-info/)
# - Python cache (__pycache__/, *.pyc, *.pyo)
# - Virtual environments (venv/, env/)
# - IDE files (.vscode/, .idea/)
# - Large generated files (unless explicitly required)
```

### 6. Offline Mode Validation
Verify that changes maintain offline compatibility:
```bash
# Key scripts should handle network failures gracefully
# Run these to verify offline mode works:
python3 gleif_echo.py
python3 gleif_alias_scan.py
python3 trust_scan_bot.py

# All should complete without crashes
# Network errors should result in mock/fallback data
```

### 7. Security Validation
```bash
# Check for exposed secrets or credentials
grep -r "password\|secret\|api_key\|token" --include="*.py" --exclude-dir=".git" .

# Ensure no hardcoded credentials in code
# Verify all sensitive data uses environment variables or config files
```

## What to Commit vs. What to Ignore

### ✅ COMMIT THESE:
- Source code files (*.py)
- Configuration files (*.json, *.yaml, *.yml) that define identifiers
- Documentation files (*.md)
- Workflow definitions (.github/workflows/*.yml)
- Requirements file (requirements.txt)
- Dashboard HTML files (*.html)

### ❌ DO NOT COMMIT THESE:
- Generated output files (output/*.json, output/*.txt)
- Generated overlay files (overlays/*.yml - these are runtime artifacts)
- Temporary XML files (gleif_echo.xml, gleif_results.xml, trust_overlay.xml)
- Archive files (archive/*.json)
- Log files (*.log, *_log.txt, failing_codes_log.txt)
- Report files (failing_codes_report.json)
- Python cache (__pycache__/, *.pyc)
- IDE configuration files

### Update .gitignore if needed:
```bash
# Add patterns to .gitignore for files that shouldn't be tracked
echo "output/*.json" >> .gitignore
echo "output/*.txt" >> .gitignore
echo "overlays/*.yml" >> .gitignore
echo "*.xml" >> .gitignore
echo "*_log.txt" >> .gitignore
echo "*_report.json" >> .gitignore
```

## Dashboard Validation

If changes affect dashboards, validate functionality:

```bash
# Start local server
python3 -m http.server 8000 &
SERVER_PID=$!

# Dashboards should be accessible at:
# - http://localhost:8000/dashboard.html
# - http://localhost:8000/syndicate_dashboard.html
# - http://localhost:8000/learning_analytics.html

# Verify dashboards load without errors in browser console
# Check that data displays correctly

# Stop server
kill $SERVER_PID
```

## GitHub Actions Validation

If changes affect workflows:

```bash
# Validate workflow YAML syntax
cd .github/workflows/
for workflow in *.yml; do
    echo "Checking $workflow..."
    python3 -c "import yaml; yaml.safe_load(open('$workflow'))" && echo "✅ Valid" || echo "❌ Invalid"
done
cd ../..
```

## Error Handling Validation

For any code changes, verify proper error handling:

### Network Failures
- Scripts should catch `NameResolutionError`, `ConnectionError`
- Provide graceful degradation with mock/sample data
- Log informative error messages
- Never crash due to network unavailability

### Missing Files
- Use `try-except` blocks when opening files
- Check file existence before operations
- Provide default values or create missing files as needed

### API Failures
- Handle API rate limits gracefully
- Provide fallback data when APIs are unavailable
- Log API errors with context

## Commit Message Guidelines

Use clear, descriptive commit messages:

```bash
# Format: <type>: <short description>

# Good examples:
# "feat: Add pre-commit validation instructions"
# "fix: Handle network errors in gleif_trace.py"
# "docs: Update README with new features"
# "refactor: Improve error handling in trust_scan_bot.py"
# "test: Add validation for offline mode"

# Types:
# - feat: New feature
# - fix: Bug fix
# - docs: Documentation changes
# - refactor: Code refactoring
# - test: Testing changes
# - chore: Maintenance tasks
```

## Integration with report_progress Tool

When using the `report_progress` tool:

1. **Before calling report_progress:**
   ```bash
   # Run validation
   python3 find_failing_codes.py
   
   # Check git status
   git status
   
   # Review changes
   git diff
   ```

2. **Provide meaningful commit message:**
   - Summarize what changed
   - Reference issue/task if applicable
   - Keep it concise but descriptive

3. **Update PR description with checklist:**
   - Mark completed items with [x]
   - Keep pending items with [ ]
   - Be accurate about progress

4. **After report_progress:**
   - Review what was committed
   - Ensure no unwanted files were included
   - Verify .gitignore is properly configured

## Quick Pre-Commit Command Sequence

For convenience, here's a complete pre-commit validation sequence:

```bash
# Quick validation sequence (copy and paste before commit)
cd /home/runner/work/Trust-identifier-trace/Trust-identifier-trace && \
python3 find_failing_codes.py && \
echo "=== Git Status ===" && \
git status && \
echo "=== Files to be committed ===" && \
git diff --cached --name-only && \
echo "=== Validation Complete ✅ ===" || \
echo "=== Validation Failed ❌ ==="
```

## Troubleshooting Common Issues

### Issue: Validation script fails
**Solution:** 
1. Check `failing_codes_log.txt` for details
2. Fix syntax/import/runtime errors in failing scripts
3. Re-run validation

### Issue: Too many files being committed
**Solution:**
1. Update .gitignore with appropriate patterns
2. Use `git rm --cached <file>` to unstage unwanted files
3. Commit the .gitignore update first

### Issue: Network-dependent tests failing
**Solution:**
- This is expected in sandboxed environments
- Verify scripts handle errors gracefully
- Check for proper fallback mechanisms

### Issue: Import errors in validation
**Solution:**
```bash
# Install missing dependencies
pip install -r requirements.txt

# Re-run validation
python3 find_failing_codes.py
```

## Performance Expectations

- **find_failing_codes.py:** 1-2 seconds
- **Individual script tests:** 1-3 seconds each
- **Dashboard validation:** 5-10 seconds
- **Complete pre-commit validation:** Under 30 seconds

**NEVER CANCEL** validation operations - they complete quickly and are essential for code quality.

## Final Checklist Before Every Commit

- [ ] Ran `python3 find_failing_codes.py` - 100% success rate ✅
- [ ] Reviewed `git status` and `git diff`
- [ ] Verified no unwanted files are staged
- [ ] Tested modified scripts execute successfully
- [ ] Checked for hardcoded secrets or credentials
- [ ] Verified offline mode compatibility maintained
- [ ] Updated .gitignore if needed
- [ ] Prepared meaningful commit message
- [ ] Ready to use report_progress tool

---

**Remember:** These validation steps are not optional. They ensure repository quality, prevent broken code, and maintain the robust offline-first design of this project.

**Automation Note:** While git hooks can automate some of these checks, this file serves as comprehensive guidance for GitHub Copilot agents to understand what validations to perform before committing code changes.
