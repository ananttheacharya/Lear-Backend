# S-06 — Secure HTTP Headers Middleware

**Owner:** Avi
**Priority:** P1
**Status:** ✅ Done — 2026-10-01
**Estimated effort:** 0.5 day
**Depends on:** Nothing
**Blocks:** Nothing

---

## Objective

Add security-focused HTTP response headers to every response from the FastAPI server. These headers instruct browsers to enable security protections like clickjacking prevention, MIME-type sniffing prevention, and strict transport security.

---

## Why This Matters

- **Currently:** The server returns zero security headers. A browser viewing any HTML response (e.g., `/demo`, admin panel) has no guidance on security policies.
- **After:** Every response includes standard security headers. This is a baseline expectation for any production web application and is checked by automated security scanners.

---

## Headers to Add

| Header | Value | Purpose |
|---|---|---|
| `X-Content-Type-Options` | `nosniff` | Prevents browser MIME-type sniffing. Forces the browser to respect the declared `Content-Type`. |
| `X-Frame-Options` | `DENY` | Prevents the page from being embedded in an iframe (clickjacking protection). |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` on HTTPS/prod only | Forces HTTPS for 1 year when the browser is already using TLS. Must not be emitted on local plain HTTP. |
| `Content-Security-Policy` | local-safe default; append `upgrade-insecure-requests` on HTTPS/prod only | Controls which resources the browser is allowed to load. Prevents XSS without breaking local HTTP/WSS development. |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Controls how much referrer info is sent with requests. |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=()` | Disables browser features the app doesn't need. |

---

## Implementation Plan

### Step 1: Create the security headers middleware

Create `prash/middleware/security_headers.py`:

```python
"""Security headers middleware.

Adds standard security headers to every HTTP response.
These are defense-in-depth measures — they don't replace proper input
validation or authentication, but they tell browsers to enforce
additional protections.
"""
from __future__ import annotations

import os
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        is_secure = request.url.scheme == "https" or request.headers.get("x-forwarded-proto") == "https"
        is_production = os.getenv("ENVIRONMENT", "").lower() == "production"
        include_transport_security = is_secure or is_production

        # Content Security Policy
        # Note: 'unsafe-inline' is needed for the demo page's inline styles/scripts
        # This should be tightened when demo pages are removed
        csp = os.getenv("LEAR_CSP", (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self' ws: wss:; "
        ))
        if include_transport_security and "upgrade-insecure-requests" not in csp:
            csp = f"{csp.rstrip('; ')}; upgrade-insecure-requests;"
        response.headers["Content-Security-Policy"] = csp

        if include_transport_security:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions policy — disable unused browser APIs
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"

        return response
```

### Step 2: Wire into the app

In `server.py` (or the app factory after B-01):

```python
from prash.middleware.security_headers import SecurityHeadersMiddleware

# Add AFTER CORSMiddleware (middleware order matters in Starlette — last added runs first)
app.add_middleware(SecurityHeadersMiddleware)
```

**Important:** Starlette/FastAPI middleware runs in LIFO order (last added, first executed). Security headers should be added after CORS so they appear on every response including CORS preflight.

### Step 3: Create CI validation script

Use the canonical cross-platform Python checker:

```bash
# Local plain HTTP should have the browser-hardening baseline, but not HSTS or
# CSP upgrade-insecure-requests because those break local HTTP/WSS development.
python scripts/security/check_security_headers.py http://localhost:8000

# HTTPS/prod deployments should include transport-security enforcement.
python scripts/security/check_security_headers.py https://example.com --expect-transport-security
```

CI should prefer focused `TestClient` tests for local/HTTPS/prod behavior rather
than starting a background uvicorn daemon only to scrape headers.

### Step 4: Write tests

Add focused tests (the implementation lives in `tests/test_security_hardening.py` in this repo):

```python
BASELINE_HEADERS = [
    "x-content-type-options",
    "x-frame-options",
    "content-security-policy",
    "referrer-policy",
    "permissions-policy",
]

def test_local_http_has_baseline_but_not_transport_upgrade(client):
    resp = client.get("/api/system/version")
    for header in BASELINE_HEADERS:
        assert header in resp.headers
    assert "strict-transport-security" not in resp.headers
    assert "upgrade-insecure-requests" not in resp.headers["content-security-policy"]

def test_https_enables_hsts_and_upgrade_insecure_requests(client):
    resp = client.get("/api/system/version", base_url="https://testserver")
    assert resp.headers["strict-transport-security"] == "max-age=31536000; includeSubDomains"
    assert "upgrade-insecure-requests" in resp.headers["content-security-policy"]
```

---

## Checklist

- [ ] Create `prash/middleware/security_headers.py` with `SecurityHeadersMiddleware`
- [ ] Add middleware to the FastAPI app (after CORS middleware)
- [ ] Verify headers appear on JSON responses (`/api/system/version`)
- [ ] Verify headers appear on HTML responses (`/demo`)
- [ ] Verify headers appear on error responses (404, 422, 500)
- [ ] Keep HSTS and CSP `upgrade-insecure-requests` disabled on local plain HTTP
- [ ] Enable HSTS and CSP `upgrade-insecure-requests` for HTTPS/proxied HTTPS or production
- [ ] Create/use canonical `scripts/security/check_security_headers.py` for validation
- [ ] Write `tests/test_security_hardening.py`
- [ ] CSP allows WebSocket connections (`connect-src 'self' ws: wss:`)
- [ ] CSP allows inline styles for demo pages (`style-src 'self' 'unsafe-inline'`)
- [ ] All existing tests pass

---

## Anti-Patterns to Avoid

> **🚫 DO NOT set CSP to be overly restrictive on the first pass.** The demo page (`/demo`, admin panel) uses inline styles and scripts. Start with `'unsafe-inline'` and tighten later when the demo pages are refactored to use external scripts.

> **🚫 DO NOT forget `connect-src` in CSP.** The desktop app uses WebSocket (`/ws/events`) and SSE (`/api/chat/stream`). Without `connect-src 'self' ws: wss:`, the CSP would block those connections.

> **🚫 DO NOT set HSTS with `preload` directive** unless you're committed to HTTPS-only forever. `preload` is permanent (browser vendors cache it). Start without it.

> **🚫 DO NOT apply headers selectively** (e.g., only on certain routes). Every response should have them. The middleware approach handles this automatically.

---

## Exit Criteria

- [ ] **Baseline headers present on every response** — JSON, HTML, error responses
- [ ] **Transport-security headers are conditional** — absent on local HTTP, present for HTTPS/prod
- [ ] **Python checker validates live servers** — `scripts/security/check_security_headers.py` exits 0
- [ ] **Tests pass** — `tests/test_security_hardening.py` covers all header values and environment cases
- [ ] **WebSocket and SSE still work** — CSP `connect-src` allows them
- [ ] **Demo pages render correctly** — CSP allows inline styles/scripts
- [ ] **All existing tests pass**
