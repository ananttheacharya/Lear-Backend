# S-03 — CORS Lockdown

**Owner:** Agrim
**Priority:** P0
**Status:** ⬜ Not Started
**Estimated effort:** 0.5 day
**Depends on:** Nothing
**Blocks:** Nothing

---

## Objective

Replace the current `allow_origins=["*"]` CORS configuration with an explicit origin allowlist. In production, only the Tauri desktop app origin is permitted. In development, `localhost:*` origins are allowed.

---

## Why This Matters

- **Currently:** `server.py` line 399–405 has `allow_origins=["*"]`, meaning ANY website in the world can make cross-origin requests to the Lear API. A malicious website could make API calls on behalf of the user if they happen to have the server running.
- **After:** Only the Tauri desktop app (and localhost during dev) can make requests. Unauthorized cross-origin requests are blocked by the browser.

---

## Current State

```python
# server.py lines 399-405
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # ← THIS IS THE PROBLEM
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Implementation Plan

### Step 1: Define allowed origins

Tauri desktop apps use `tauri://localhost` or `https://tauri.localhost` as their origin (depends on Tauri version). Check the actual origin the desktop app sends:

```python
# prash/middleware/cors.py
import os

def get_allowed_origins() -> list[str]:
    """Build the CORS allowlist based on environment."""
    env = os.getenv("LEAR_ENV", "development")

    # Tauri app origins — always allowed
    origins = [
        "tauri://localhost",
        "https://tauri.localhost",
    ]

    if env == "development":
        # Dev: allow any localhost port (Vite dev server, etc.)
        # Note: CORSMiddleware supports regex via allow_origin_regex
        origins.extend([
            "http://localhost:1420",   # Vite default (Tauri dev)
            "http://localhost:3000",   # Common dev port
            "http://localhost:5173",   # Vite default
            "http://localhost:8080",   # Common dev port
            "http://127.0.0.1:1420",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:8080",
        ])

    # Allow override for custom deployments
    extra = os.getenv("LEAR_CORS_ORIGINS", "")
    if extra:
        origins.extend(o.strip() for o in extra.split(",") if o.strip())

    return origins
```

### Step 2: Update CORSMiddleware configuration

```python
from prash.middleware.cors import get_allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
)
```

**Also tighten:**
- `allow_methods` — enumerate the methods actually used instead of `["*"]`
- `allow_headers` — enumerate the headers actually sent instead of `["*"]`

### Step 3: Handle development convenience

For the common case where someone is developing and forgets to set `LEAR_ENV`, default to `development` so local dev works out of the box. Log a warning if `allow_origins=["*"]` would have been needed:

```python
import logging
logger = logging.getLogger(__name__)

origins = get_allowed_origins()
logger.info(f"CORS allowed origins: {origins}")
```

### Step 4: Write tests

Create `tests/test_cors.py`:

```python
"""CORS lockdown tests."""
import pytest
from fastapi.testclient import TestClient

def test_allowed_origin_receives_cors_headers(client):
    """Request from Tauri origin should include CORS headers."""
    resp = client.get(
        "/api/system/version",
        headers={"Origin": "tauri://localhost"}
    )
    assert resp.headers.get("access-control-allow-origin") == "tauri://localhost"

def test_disallowed_origin_blocked(client):
    """Request from unauthorized origin should NOT include CORS headers."""
    resp = client.get(
        "/api/system/version",
        headers={"Origin": "https://evil.example.com"}
    )
    # FastAPI's CORSMiddleware simply omits the header for disallowed origins
    assert "access-control-allow-origin" not in resp.headers or \
           resp.headers["access-control-allow-origin"] != "https://evil.example.com"

def test_preflight_from_allowed_origin(client):
    """OPTIONS preflight from allowed origin should succeed."""
    resp = client.options(
        "/api/connectors",
        headers={
            "Origin": "tauri://localhost",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        }
    )
    assert resp.status_code == 200
    assert resp.headers.get("access-control-allow-origin") == "tauri://localhost"

def test_preflight_from_disallowed_origin(client):
    """OPTIONS preflight from unauthorized origin should be rejected."""
    resp = client.options(
        "/api/connectors",
        headers={
            "Origin": "https://evil.example.com",
            "Access-Control-Request-Method": "POST",
        }
    )
    assert "access-control-allow-origin" not in resp.headers or \
           resp.headers["access-control-allow-origin"] != "https://evil.example.com"

def test_localhost_allowed_in_dev(client, monkeypatch):
    """In development mode, localhost origins should be allowed."""
    monkeypatch.setenv("LEAR_ENV", "development")
    resp = client.get(
        "/api/system/version",
        headers={"Origin": "http://localhost:5173"}
    )
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:5173"
```

---

## Checklist

- [ ] Identify the exact Tauri app origin(s) — check `tauri.conf.json` and actual request headers
- [ ] Create `prash/middleware/cors.py` with `get_allowed_origins()`
- [ ] Update `CORSMiddleware` configuration to use explicit origin list
- [ ] Tighten `allow_methods` to only methods actually used
- [ ] Tighten `allow_headers` to only headers actually sent by the desktop app
- [ ] Add `LEAR_CORS_ORIGINS` env var support for custom deployments
- [ ] Add `LEAR_ENV` environment detection (default: `development`)
- [ ] Log the allowed origins at startup for debuggability
- [ ] Write `tests/test_cors.py` with allowed/blocked/preflight tests
- [ ] Verify the Tauri desktop app still works (manual test)
- [ ] All existing tests pass

---

## Anti-Patterns to Avoid

> **🚫 DO NOT use `allow_origin_regex=".*localhost.*"` in production.** Regex origins are powerful but dangerous — a typo can open the whole allowlist. Use explicit strings.

> **🚫 DO NOT forget about Tauri's origin format.** Tauri 2.x uses `https://tauri.localhost` by default, but Tauri 1.x used `tauri://localhost`. Check which version this project uses (`desktop/src-tauri/tauri.conf.json`).

> **🚫 DO NOT hardcode port numbers without the env var escape hatch.** Developers run Vite on different ports. The `LEAR_CORS_ORIGINS` env var handles this.

> **🚫 DO NOT break the existing test client.** `TestClient` from `httpx`/`starlette` doesn't send an `Origin` header by default, so existing tests should be unaffected. Verify this explicitly.

---

## Exit Criteria

- [ ] **`CORSMiddleware` configured with explicit origins** — `allow_origins=["*"]` is gone
- [ ] **Cross-origin request from unauthorized origin is blocked** — test proves it
- [ ] **Tauri desktop app still works** — manual smoke test
- [ ] **Preflight (OPTIONS) requests handled correctly** for allowed origins
- [ ] **All existing tests pass** without modification
