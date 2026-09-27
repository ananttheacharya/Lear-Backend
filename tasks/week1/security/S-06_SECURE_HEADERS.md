# S-06 — Secure HTTP Headers Middleware

**Owner:** Parv
**Priority:** P1
**Status:** ⬜ Not Started
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
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | Forces HTTPS for 1 year. Only effective when served over HTTPS. |
| `Content-Security-Policy` | `default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'` | Controls which resources the browser is allowed to load. Prevents XSS. |
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

        # Force HTTPS (only meaningful when behind TLS termination)
        # In dev, this is harmless — browsers ignore it on localhost HTTP
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

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
        response.headers["Content-Security-Policy"] = csp

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

Create `scripts/check_security_headers.sh` (or `.ps1` for Windows):

```bash
#!/bin/bash
# Validate that all security headers are present on API responses.
# Run against a live server: ./scripts/check_security_headers.sh http://localhost:8000

BASE_URL="${1:-http://localhost:8000}"

echo "Checking security headers on $BASE_URL/api/system/version"
HEADERS=$(curl -sI "$BASE_URL/api/system/version")

check_header() {
    local header="$1"
    if echo "$HEADERS" | grep -qi "$header"; then
        echo "  ✅ $header"
    else
        echo "  ❌ $header — MISSING"
        FAIL=1
    fi
}

check_header "X-Content-Type-Options"
check_header "X-Frame-Options"
check_header "Strict-Transport-Security"
check_header "Content-Security-Policy"
check_header "Referrer-Policy"
check_header "Permissions-Policy"

if [ "$FAIL" = "1" ]; then
    echo ""
    echo "FAILED: Some security headers are missing."
    exit 1
else
    echo ""
    echo "All security headers present."
fi
```

### Step 4: Write tests

Add to `tests/test_security_headers.py`:

```python
"""Security headers tests — verify all headers on every response type."""
import pytest

REQUIRED_HEADERS = [
    "x-content-type-options",
    "x-frame-options",
    "strict-transport-security",
    "content-security-policy",
    "referrer-policy",
    "permissions-policy",
]

def test_security_headers_on_json_endpoint(client):
    """JSON API responses include all security headers."""
    resp = client.get("/api/system/version")
    for header in REQUIRED_HEADERS:
        assert header in resp.headers, f"Missing header: {header}"

def test_security_headers_on_html_endpoint(client):
    """HTML responses (demo page) include all security headers."""
    resp = client.get("/demo")
    for header in REQUIRED_HEADERS:
        assert header in resp.headers, f"Missing header: {header}"

def test_x_content_type_options_value(client):
    resp = client.get("/api/system/version")
    assert resp.headers["x-content-type-options"] == "nosniff"

def test_x_frame_options_value(client):
    resp = client.get("/api/system/version")
    assert resp.headers["x-frame-options"] == "DENY"

def test_hsts_value(client):
    resp = client.get("/api/system/version")
    assert "max-age=" in resp.headers["strict-transport-security"]
```

---

## Checklist

- [ ] Create `prash/middleware/security_headers.py` with `SecurityHeadersMiddleware`
- [ ] Add middleware to the FastAPI app (after CORS middleware)
- [ ] Verify headers appear on JSON responses (`/api/system/version`)
- [ ] Verify headers appear on HTML responses (`/demo`)
- [ ] Verify headers appear on error responses (404, 422, 500)
- [ ] Create `scripts/check_security_headers.sh` for CI validation
- [ ] Write `tests/test_security_headers.py`
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

- [ ] **All 6 headers present on every response** — JSON, HTML, error responses
- [ ] **`curl -I` test script in CI validates** — `scripts/check_security_headers.sh` exits 0
- [ ] **Tests pass** — `tests/test_security_headers.py` covers all header values
- [ ] **WebSocket and SSE still work** — CSP `connect-src` allows them
- [ ] **Demo pages render correctly** — CSP allows inline styles/scripts
- [ ] **All existing tests pass**
