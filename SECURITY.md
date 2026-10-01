# Security Policy

Lear is a local-first DevOps agent. Credentials must stay on the operator's
machine and must never be committed to the repository.

## Reporting a vulnerability

If you find a vulnerability or accidental secret exposure, do **not** open a
public issue with secret values. Send the minimal reproduction and affected
paths to the maintainers through the team's private security channel. Include
whether the credential has already been rotated.

## Local secret-leak protection

Install the committed hook once per clone:

```bash
python scripts/security/install_hooks.py
```

The hook runs `gitleaks protect --staged` when `gitleaks` is available and then
runs Lear's bundled fallback scanner. The fallback scanner redacts findings and
exists so contributors are still protected before they install the full gitleaks
binary.

Manual scans:

```bash
# One command, portable fallback scanner
python scripts/security/verify_security_hardening.py

# Working tree only
python scripts/security/secrets_audit.py --working-tree

# Full reachable git history
python scripts/security/secrets_audit.py --history

# Preferred when gitleaks is installed
gitleaks detect --source . --config .gitleaks.toml --redact --verbose

# Bash / PowerShell wrappers
scripts/security/run_secret_audit.sh
./scripts/security/run_secret_audit.ps1
```

Do not commit raw `gitleaks-report.json` files. They can reveal sensitive file
locations and excerpts; report patterns are ignored by `.gitignore`.

## HTTP response header baseline

The FastAPI bridge applies the S-06 browser hardening headers from
`prash.middleware.security_headers.SecurityHeadersMiddleware` to every HTTP
response. Validate a running server with:

```bash
scripts/check_security_headers.sh http://localhost:8000
```

The current default Content Security Policy intentionally allows inline scripts
and styles because the demo/admin HTML pages still use inline assets. Production
deployments that have externalized those assets can set `LEAR_CSP` to a stricter
policy without code changes.

## Credential handling rules

- Keep real credentials in `.env`, never in source files, docs, screenshots, or
  test fixtures.
- Use obvious placeholders (`placeholder`, `example`, `fake`, `test-only`) in
  docs/tests instead of realistic provider token prefixes.
- Rotate any credential that may have been committed or pasted into a public
  channel.
- Prefer narrow provider scopes and short-lived credentials where providers
  support them.
