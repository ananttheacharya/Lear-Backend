# Security Reviewer Quickstart

This page is the shortest path for a reviewer to verify the S-05/S-06 work on a
fresh checkout of this branch.

## 1. Confirm you are on the security branch

```bash
git branch --show-current
git rev-list --left-right --count origin/main...HEAD
```

Expected: the branch is `arena/01a0f7f6-lear-backend-avi` and is ahead of
`origin/main`.

## 2. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## 3. Install the local pre-commit hook

```bash
python scripts/security/install_hooks.py
```

This sets `core.hooksPath=.githooks` for this clone.

## 4. Run the one-command security verification

Fast smoke test:

```bash
python scripts/security/verify_security_hardening.py --skip-history
```

Full local verification:

```bash
python scripts/security/verify_security_hardening.py
```

If you have the upstream `gitleaks` binary installed, also run:

```bash
gitleaks detect --source . --config .gitleaks.toml --redact --verbose
```

## 5. Verify HTTP headers against a live server

Terminal 1:

```bash
python -m uvicorn prash.server:app --host 127.0.0.1 --port 8000
```

Terminal 2:

```bash
scripts/check_security_headers.sh http://127.0.0.1:8000
python scripts/security/check_security_headers.py http://127.0.0.1:8000
```

Windows PowerShell alternative:

```powershell
./scripts/check_security_headers.ps1 http://127.0.0.1:8000
```

## 6. Focused tests

```bash
pytest -q tests/test_security_hardening.py
```

## Expected result

- Secret scans report zero findings.
- Security header checks report all required headers present.
- Focused tests pass.
- Pre-commit blocks staged provider-token patterns before a commit is created.
