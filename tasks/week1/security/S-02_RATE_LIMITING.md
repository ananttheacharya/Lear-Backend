# S-02 — Rate Limiting Middleware

**Owner:** Parv
**Priority:** P0
**Status:** ⬜ Not Started
**Estimated effort:** 1–2 days
**Depends on:** Nothing (can start immediately, but easier after B-01 route split)
**Blocks:** Nothing

---

## Objective

Add rate limiting middleware to the FastAPI backend. Implement per-IP rate limits on auth-sensitive endpoints and a global rate limit on all endpoints. Exceeding the limit must return `429 Too Many Requests` with a `Retry-After` header.

---

## Why This Matters

- **Currently:** Every endpoint accepts unlimited requests. A single client can flood the server, causing denial of service for other users, or brute-force connector credentials via `/api/connectors/{id}/connect`.
- **After:** Auth-sensitive endpoints have tight limits (e.g., 10 req/min). Other endpoints have a reasonable global cap. The server stays responsive under abuse.

---

## Current State

- No rate limiting exists anywhere in the codebase
- `server.py` (line 397–405) has only the `CORSMiddleware` — no other middleware
- The app is single-user local-first, but the API is network-exposed when the desktop app runs

---

## Implementation Plan

### Step 1: Choose and install the rate limiting library

Use **`slowapi`** — it's the de facto rate limiter for FastAPI, built on `limits`.

```bash
pip install slowapi
```

Add to `requirements.txt` / `pyproject.toml`.

### Step 2: Create rate limiting configuration

Create `prash/middleware/rate_limit.py`:

```python
"""Rate limiting middleware configuration.

Tiered rate limits:
- Auth-sensitive endpoints:  10 requests/minute per IP
- Chat/streaming endpoints:  30 requests/minute per IP
- General API endpoints:    120 requests/minute per IP
"""
from __future__ import annotations

import os
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse

# Allow override via environment for dev/testing
AUTH_RATE_LIMIT = os.getenv("LEAR_RATE_LIMIT_AUTH", "10/minute")
CHAT_RATE_LIMIT = os.getenv("LEAR_RATE_LIMIT_CHAT", "30/minute")
GLOBAL_RATE_LIMIT = os.getenv("LEAR_RATE_LIMIT_GLOBAL", "120/minute")

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[GLOBAL_RATE_LIMIT],
    storage_uri="memory://",  # In-memory for single-instance; swap to Redis for multi-instance
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Return a structured 429 response with Retry-After header."""
    retry_after = getattr(exc, "retry_after", 60)
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": f"Rate limit exceeded. Try again in {retry_after} seconds.",
            "retry_after": retry_after,
        },
        headers={"Retry-After": str(retry_after)},
    )
```

### Step 3: Apply to auth-sensitive endpoints

These endpoints are the highest risk for abuse:

| Endpoint | Why it's sensitive | Limit |
|---|---|---|
| `POST /api/connectors/{id}/connect` | Credential submission — brute-force target | 10/minute |
| `POST /api/chat/stream` | LLM call — expensive compute | 30/minute |
| `POST /api/chat/execute` | Action execution — can modify external systems | 10/minute |
| `POST /api/chat` | LLM call | 30/minute |
| `POST /api/connect/{service_id}` | Legacy connector auth | 10/minute |

Apply the decorator:

```python
from prash.middleware.rate_limit import limiter, AUTH_RATE_LIMIT, CHAT_RATE_LIMIT

@app.post("/api/connectors/{connector_id}/connect")
@limiter.limit(AUTH_RATE_LIMIT)
async def connect_connector(request: Request, connector_id: str, ...):
    ...

@app.post("/api/chat/stream")
@limiter.limit(CHAT_RATE_LIMIT)
async def chat_stream(request: Request, ...):
    ...
```

### Step 4: Wire into the FastAPI app

In `server.py` (or the app factory after B-01):

```python
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from prash.middleware.rate_limit import limiter, rate_limit_exceeded_handler

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
```

### Step 5: Write integration tests

Create `tests/test_rate_limiting.py`:

```python
"""Rate limiting integration tests."""
import pytest
from fastapi.testclient import TestClient

def test_rate_limit_returns_429_on_exceed(client):
    """Exceed the auth endpoint rate limit, expect 429."""
    # The auth limit is 10/minute — send 11 requests
    for i in range(10):
        resp = client.post("/api/connectors/github/connect", json={"credentials": {"GITHUB_TOKEN": "fake"}})
        # We don't care about 400/401 — just not 429 yet
        assert resp.status_code != 429, f"Rate limited too early on request {i+1}"

    # The 11th should be rate limited
    resp = client.post("/api/connectors/github/connect", json={"credentials": {"GITHUB_TOKEN": "fake"}})
    assert resp.status_code == 429

def test_rate_limit_includes_retry_after_header(client):
    """429 response must include Retry-After header."""
    # Exceed limit
    for _ in range(11):
        client.post("/api/connectors/github/connect", json={"credentials": {"GITHUB_TOKEN": "fake"}})

    resp = client.post("/api/connectors/github/connect", json={"credentials": {"GITHUB_TOKEN": "fake"}})
    assert resp.status_code == 429
    assert "Retry-After" in resp.headers
    assert int(resp.headers["Retry-After"]) > 0

def test_rate_limit_body_structure(client):
    """429 response body must be structured JSON."""
    for _ in range(11):
        client.post("/api/connectors/github/connect", json={"credentials": {"GITHUB_TOKEN": "fake"}})

    resp = client.post("/api/connectors/github/connect", json={"credentials": {"GITHUB_TOKEN": "fake"}})
    body = resp.json()
    assert body["error"] == "rate_limit_exceeded"
    assert "retry_after" in body
    assert "message" in body

def test_global_rate_limit_does_not_block_normal_usage(client):
    """Normal usage patterns should not trigger the global limit."""
    # 50 GET requests should be well under 120/min
    for _ in range(50):
        resp = client.get("/api/system/version")
        assert resp.status_code != 429
```

---

## Checklist

### Preparation
- [ ] Install `slowapi` and add to project dependencies
- [ ] Read `slowapi` docs for FastAPI integration pattern

### Implementation
- [ ] Create `prash/middleware/__init__.py`
- [ ] Create `prash/middleware/rate_limit.py` with tiered rate limit configuration
- [ ] Wire limiter into the FastAPI app (`app.state.limiter`, exception handler)
- [ ] Apply `@limiter.limit(AUTH_RATE_LIMIT)` to auth-sensitive endpoints
- [ ] Apply `@limiter.limit(CHAT_RATE_LIMIT)` to chat/LLM endpoints
- [ ] Confirm global default limit applies to all other endpoints
- [ ] Confirm `429` responses include `Retry-After` header
- [ ] Confirm `429` response body is structured JSON (not raw text)

### Testing
- [ ] `tests/test_rate_limiting.py` with tests for each tier
- [ ] Integration test: exceed auth limit → 429
- [ ] Integration test: exceed chat limit → 429
- [ ] Integration test: normal usage stays under global limit
- [ ] Integration test: `Retry-After` header present and valid
- [ ] All existing tests pass (rate limiter doesn't interfere)

---

## Anti-Patterns to Avoid

> **🚫 DO NOT hardcode rate limit values.** Use env vars (`LEAR_RATE_LIMIT_AUTH`, etc.) with sensible defaults. Tests and dev environments need different limits than production.

> **🚫 DO NOT use Redis storage for now.** The app is single-instance local-first. Use `memory://` storage. Add a comment noting Redis is needed for multi-instance scaling (Week 3).

> **🚫 DO NOT rate-limit health check endpoints.** `GET /api/system/version` and similar status endpoints should be exempt or have very high limits — load balancers poll these.

> **🚫 DO NOT forget to pass `request: Request` as the first parameter** to every rate-limited endpoint. `slowapi` needs it to extract the client IP. If the endpoint doesn't already have `request`, add it.

> **🚫 DO NOT apply rate limiting to WebSocket endpoints.** `slowapi` doesn't support WebSocket rate limiting. WS abuse prevention is covered by S-07 (WebSocket auth).

---

## Exit Criteria

- [ ] **Rate limiter active** — `slowapi` middleware installed and wired
- [ ] **Auth-sensitive endpoints limited** to 10 req/min per IP
- [ ] **Chat/LLM endpoints limited** to 30 req/min per IP
- [ ] **Global limit** of 120 req/min per IP on all other endpoints
- [ ] **Exceeding limit returns 429** with `Retry-After` header
- [ ] **Integration test proves it** — `tests/test_rate_limiting.py` passes
- [ ] **All 800+ existing tests pass** without modification
