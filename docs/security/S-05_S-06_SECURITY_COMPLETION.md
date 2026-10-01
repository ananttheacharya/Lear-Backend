# S-05 / S-06 Security Completion Report

**Date:** 2026-10-01  
**Branch:** `arena/01a0f7f6-lear-backend-avi`  
**Scope:** S-05 secrets audit and S-06 secure HTTP response headers.

## Summary

This change set adds two production-grade security controls without changing endpoint behavior:

1. **S-05 — Secrets audit and prevention**
   - Added gitleaks configuration and ignore scaffolding.
   - Added a versioned pre-commit hook that runs `gitleaks protect --staged` when the binary is installed.
   - Added a bundled redacted fallback scanner so staged provider-token patterns are still blocked on machines without `gitleaks`.
   - Replaced realistic-looking unit-test token strings with clear non-secret placeholders.
   - Installed the hook locally with `core.hooksPath=.githooks`.
   - Verified the hook blocks a staged fake provider secret.

2. **S-06 — Secure HTTP headers**
   - Added ASGI-level `SecurityHeadersMiddleware` to `prash.server`.
   - Headers are injected at the raw `http.response.start` event, covering JSON responses, HTML pages, streaming/SSE responses, CORS/preflight responses, and handled API errors.
   - Added automated tests for JSON, HTML, and handled error responses.
   - Added a curl validation script for live-server checks.

## Prior security posture

Before this work:

- The repo had a Gitleaks connector for scanning other repositories, but no committed guardrail for scanning this repository before commits.
- Developers could commit realistic-looking tokens in tests or docs without a local hook blocking them.
- FastAPI responses did not consistently set browser hardening headers.
- Clean installs could fail collecting `prash.server` tests because `/api/chat/upload` uses FastAPI `File()` without `python-multipart` declared.

## What changed

### Secret scanning and leak prevention

Added:

- `.gitleaks.toml`
- `.gitleaksignore`
- `.pre-commit-config.yaml`
- `.githooks/pre-commit`
- `scripts/security/install_hooks.py`
- `scripts/security/secrets_audit.py`
- `tests/test_security_hardening.py`

The committed hook runs in this order:

1. If `gitleaks` is installed, run:

   ```bash
   gitleaks protect --staged --redact --config .gitleaks.toml --verbose
   ```

2. Always run Lear's fallback scanner:

   ```bash
   python scripts/security/secrets_audit.py --staged
   ```

The fallback scanner emits only redacted excerpts and detects common provider-token families including AWS, GitHub, GitLab, Slack, Google, OpenAI-compatible keys, private keys, and Lear-specific provider secret assignments.

### Secure headers

Every HTTP response now receives:

| Header | Value |
|---|---|
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` |
| `Content-Security-Policy` | compatible default policy for the current inline demo/admin pages |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=()` |

The CSP is intentionally compatible with the existing demo/admin HTML surfaces, which still use inline scripts/styles. Deployments can tighten it with `LEAR_CSP` after those pages move to external assets.

## What could not be changed here

- The sandbox could not download the upstream `gitleaks` binary from GitHub release assets. Multiple attempts through `gh release download`, `curl`, `wget`, and `gh api` failed with release-asset EOF/TLS termination errors.
- Because of that environment limitation, the committed hook/config is ready for real `gitleaks`, but this run used the bundled redacted fallback scanner for local full-history verification.
- Historical fake fixture literals in the existing upstream commit cannot be erased with a normal forward commit. Rewriting shared git history would be disruptive and is explicitly discouraged by the task guide unless a real production secret is confirmed. Instead, current HEAD replaces those literals, and the scanner exact-allowlists only known fake historical fixture values.

## Verification performed

```bash
python scripts/security/install_hooks.py
python scripts/security/secrets_audit.py --working-tree --report /tmp/lear-working-secret-report.json
python scripts/security/secrets_audit.py --history --report /tmp/lear-history-secret-report.json
scripts/check_security_headers.sh http://127.0.0.1:8000
pytest -q tests/test_security_hardening.py tests/test_desktop_api.py::test_CONFIG_MASKED_CREDENTIALS tests/test_desktop_api.py::test_SYSTEM_VERSION_DYNAMIC tests/test_gitleaks_connector.py::test_poll_state_never_leaks_the_actual_secret_value
```

Results:

- Working-tree secret scan: **0 findings**.
- Full-history fallback scan: **0 findings**.
- Pre-commit hook fake-secret probe: **blocked** with redacted output.
- Live HTTP header script: **all six headers present**.
- Targeted tests: **8 passed**.

A broader local run of `tests/test_desktop_api.py tests/test_gitleaks_connector.py tests/test_security_hardening.py` passed 45 tests and surfaced two pre-existing chat/LLM test failures unrelated to S-05/S-06. They are documented in `PRASH_V2.md` rather than hidden.

## Why this is stronger now

- Security headers are centralized in ASGI middleware, not copied route-by-route.
- Secret prevention is layered: gitleaks when available plus a repo-local fallback scanner.
- Reports and console output are redacted by design.
- Hook installation is documented and one command.
- Test fixtures no longer need realistic-looking provider tokens to prove masking behavior.
- The implementation stays local-first: no secret data is sent to a third-party service.
