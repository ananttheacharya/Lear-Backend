# S-05 — Secrets Audit: Scan Codebase for Leaked Patterns

**Owner:** Parv
**Priority:** P0
**Status:** ⬜ Not Started
**Estimated effort:** 0.5 day
**Depends on:** Nothing (can start immediately — should be one of the first tasks)
**Blocks:** Nothing (but should finish before any other PR merges)

---

## Objective

Run `gitleaks` against the full git history to detect any leaked secrets (API keys, tokens, passwords). Fix all findings. Install a pre-commit hook to prevent future leaks.

---

## Why This Matters

- **Currently:** The project handles credentials for 14 connectors (AWS, GitHub, GitLab, Datadog, PagerDuty, Grafana, Snyk, etc.). There's a risk that a key was accidentally committed at some point in the repo's history. Even if rotated, the key is in the git log forever unless the history is rewritten.
- **After:** A clean audit trail. A pre-commit hook ensures no new leaks slip through.

---

## Current State

- The project already has a `gitleaks` connector (`connectors/gitleaks.py`) that scans OTHER repos for leaks — but nobody has scanned THIS repo
- `.env` is in `.gitignore` — but `.env.example`, test fixtures, and old commits might contain real values
- Credentials are handled in `prash/credentials.py` (2.5 KB) and `prash/connector_registry.py` (38 KB)

---

## Implementation Plan

### Step 1: Install gitleaks

```bash
# macOS
brew install gitleaks

# Windows (scoop)
scoop install gitleaks

# Or download from GitHub releases
# https://github.com/gitleaks/gitleaks/releases
```

### Step 2: Run full history scan

```bash
# From repo root
gitleaks detect --source . --verbose --report-format json --report-path gitleaks-report.json
```

This scans EVERY commit in the git history, not just the working tree.

### Step 3: Triage findings

For each finding in the report:

1. **Determine if it's a real secret or a false positive**
   - Test keys in examples/docs → false positive (but still fix if they look real)
   - Base64-encoded strings → check if they decode to anything sensitive
   - API keys in test fixtures → if they're real, rotate immediately; if they're fake test values, add to `.gitleaksignore`

2. **If it's a real leaked secret:**
   - **Rotate the credential immediately** on the provider's website
   - Note the commit hash and file where it was found
   - Decide whether to rewrite git history (usually not worth it for a private repo — just rotate)

3. **If it's a false positive:**
   - Add to `.gitleaksignore` with a comment explaining why

### Step 4: Create `.gitleaksignore`

```toml
# .gitleaksignore
# False positives from the gitleaks scan.
# Each entry is a finding fingerprint from the gitleaks report.

# Test fixture: fake AWS key in test_aws_connector.py (not a real credential)
<fingerprint-hash-here>

# Example .env template values
<fingerprint-hash-here>
```

### Step 5: Create `.gitleaks.toml` config

```toml
# .gitleaks.toml
title = "Lear Backend Gitleaks Config"

[allowlist]
  description = "Known non-secrets"
  paths = [
    '''\.gitleaksignore''',
    '''\.env\.example''',
  ]

# Custom rules can extend the defaults
# [[rules]]
#   id = "lear-custom-pattern"
#   description = "Custom API key pattern"
#   regex = '''LEAR_[A-Z_]+_KEY\s*=\s*['"]?[a-zA-Z0-9]{32,}['"]?'''
```

### Step 6: Install pre-commit hook

Option A — using `pre-commit` framework (recommended):

```bash
pip install pre-commit
```

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.4  # Use latest stable
    hooks:
      - id: gitleaks
```

Install the hook:

```bash
pre-commit install
```

Option B — standalone git hook (if `pre-commit` framework not desired):

Create `.git/hooks/pre-commit`:

```bash
#!/bin/sh
# Gitleaks pre-commit hook — blocks commits containing secrets
gitleaks protect --staged --verbose
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Gitleaks found potential secrets in staged files."
    echo "   Fix the findings above, or use 'git commit --no-verify' to bypass (not recommended)."
    exit 1
fi
```

### Step 7: Verify the fix

```bash
# Re-run scan — should return 0 findings on HEAD
gitleaks detect --source . --verbose
echo $?  # Must be 0

# Test the pre-commit hook
echo "FAKE_API_KEY=sk-1234567890abcdef" > test_leak.txt
git add test_leak.txt
git commit -m "test"  # Should be BLOCKED by gitleaks
rm test_leak.txt
git reset HEAD test_leak.txt
```

---

## Checklist

### Scan
- [ ] Install `gitleaks` (verify version: `gitleaks version`)
- [ ] Run `gitleaks detect --source . --verbose --report-format json --report-path gitleaks-report.json`
- [ ] Review every finding in the report
- [ ] Classify each as: real leak, false positive, or test fixture

### Remediation
- [ ] Rotate any real leaked credentials on the provider's website
- [ ] Create `.gitleaksignore` for false positives (with comments explaining each)
- [ ] Create `.gitleaks.toml` with project-specific configuration
- [ ] Re-run scan and confirm 0 findings: `gitleaks detect --source .` exits 0

### Prevention
- [ ] Install pre-commit hook (either `pre-commit` framework or standalone git hook)
- [ ] Test the hook: stage a file with a fake secret, verify commit is blocked
- [ ] Document the hook in the project README or CONTRIBUTING.md

### Documentation
- [ ] PR description lists all findings and their remediation
- [ ] Note which credentials were rotated (without revealing the old values)

---

## Anti-Patterns to Avoid

> **🚫 DO NOT commit the `gitleaks-report.json` file.** It contains finding details that could reveal secret locations. Delete it or add to `.gitignore`.

> **🚫 DO NOT rewrite git history** unless there's a confirmed leaked production secret in a public repo. History rewriting is disruptive for all team members. Rotation is sufficient for private repos.

> **🚫 DO NOT disable gitleaks for entire files.** If a test file has fake API keys, either make them obviously fake (e.g., `FAKE_KEY_FOR_TESTING_DO_NOT_USE`) or add the specific finding fingerprint to `.gitleaksignore` — not a blanket file exclusion.

> **🚫 DO NOT use `--no-verify` to bypass the pre-commit hook in normal workflow.** If the hook blocks a commit, fix the finding. `--no-verify` is only for emergency situations.

> **🚫 DO NOT mark findings as false positives without checking.** If something looks like an API key, verify it's not real before dismissing it. When in doubt, rotate it.

---

## Exit Criteria

- [ ] **`gitleaks detect --source .` returns 0 findings on HEAD** — clean scan
- [ ] **Pre-commit hook installed and working** — test confirms it blocks a staged secret
- [ ] **Any real leaked credentials have been rotated** on the provider's website
- [ ] **`.gitleaksignore` + `.gitleaks.toml`** committed with documented exclusions
- [ ] **Hook documented** in README or CONTRIBUTING.md
