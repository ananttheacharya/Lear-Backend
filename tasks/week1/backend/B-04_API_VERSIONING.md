# B-04 — API Versioning

**Owner:** Parv
**Priority:** P2
**Status:** ⬜ Not Started
**Estimated effort:** 1 day
**Depends on:** B-01 (route modules exist as APIRouters)
**Blocks:** Nothing

---

## Objective

Prefix all API endpoints with `/api/v1/`. Maintain backward compatibility by keeping the existing `/api/...` paths as redirects. Prepare the pattern for future `/api/v2/` without breaking existing desktop app clients.

---

## Why This Matters

- **Currently:** Endpoints live under `/api/...` with no version prefix. Any breaking change to an endpoint requires coordinating backend and desktop app deployments simultaneously. There's no way to run an old desktop app against a new backend.
- **After:** The canonical path is `/api/v1/...`. The legacy `/api/...` paths redirect to v1. The desktop app is updated to call `/api/v1/...` directly. Adding v2 later is straightforward.

---

## Implementation Plan

### Step 1: Add version prefix to all routers

After B-01, each route module has an `APIRouter`. Update their prefix:

```python
# prash/routes/connectors.py
# Before:
router = APIRouter(prefix="/api", tags=["connectors"])

# After:
router = APIRouter(prefix="/api/v1", tags=["connectors"])
```

### Step 2: Create legacy redirect middleware

```python
# prash/middleware/api_versioning.py
"""Redirect unversioned /api/... to /api/v1/... for backward compatibility."""
from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
import re


class APIVersionRedirectMiddleware(BaseHTTPMiddleware):
    """Redirect /api/... (without version) to /api/v1/...
    
    This allows old desktop app versions to keep working while
    new versions call /api/v1/... directly.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path = request.url.path

        # Only redirect /api/... that doesn't already have a version
        if path.startswith("/api/") and not re.match(r"/api/v\d+/", path):
            # Redirect to /api/v1/...
            new_path = "/api/v1/" + path[len("/api/"):]
            # Use 307 to preserve the HTTP method (POST stays POST)
            return RedirectResponse(
                url=new_path + ("?" + request.url.query if request.url.query else ""),
                status_code=307,
            )

        return await call_next(request)
```

### Step 3: Add version negotiation header

```python
# In the security headers middleware or a dedicated response middleware
response.headers["X-API-Version"] = "v1"
```

### Step 4: Update the desktop app

In the desktop app's API client configuration, update the base URL:

```typescript
// Before:
const API_BASE = "http://localhost:8000/api";

// After:
const API_BASE = "http://localhost:8000/api/v1";
```

Search for all `/api/` references in the desktop codebase and update them.

### Step 5: Write tests

```python
def test_versioned_endpoint_responds(client):
    """Canonical /api/v1/... path works."""
    resp = client.get("/api/v1/system/version")
    assert resp.status_code == 200

def test_unversioned_endpoint_redirects(client):
    """Legacy /api/... path redirects to /api/v1/..."""
    resp = client.get("/api/system/version", follow_redirects=False)
    assert resp.status_code == 307
    assert "/api/v1/system/version" in resp.headers["location"]

def test_post_redirect_preserves_method(client):
    """307 redirect preserves POST method (not 301/302 which downgrade to GET)."""
    resp = client.post("/api/chat", json={"message": "hi"}, follow_redirects=False)
    assert resp.status_code == 307

def test_api_version_header(client):
    """Responses include X-API-Version header."""
    resp = client.get("/api/v1/system/version")
    assert resp.headers.get("x-api-version") == "v1"
```

---

## Checklist

- [ ] Wait for B-01 to complete (route modules as APIRouters)
- [ ] Update all router prefixes from `/api` to `/api/v1`
- [ ] Create `APIVersionRedirectMiddleware` for backward compatibility
- [ ] Use HTTP `307 Temporary Redirect` (preserves method) not `301`/`302`
- [ ] Add `X-API-Version` response header
- [ ] Update desktop app API base URL to `/api/v1`
- [ ] Update all desktop `fetch()` calls to use versioned paths
- [ ] Non-API routes (`/demo`, `/store`, `/admin`, `/ws/events`) are NOT versioned
- [ ] Write redirect and versioned-path tests
- [ ] All existing tests pass (update test URLs if needed)

---

## Anti-Patterns to Avoid

> **🚫 DO NOT use 301 or 302 redirects.** These cause browsers/clients to downgrade POST/PUT/DELETE to GET. Use `307 Temporary Redirect` which preserves the original HTTP method.

> **🚫 DO NOT version non-API routes.** `/demo`, `/store`, `/admin`, `/ws/events`, and static file routes should NOT have version prefixes.

> **🚫 DO NOT duplicate route registrations** (registering every route under both `/api/v1/` and `/api/`). Use the redirect middleware instead — one source of truth.

> **🚫 DO NOT add version to the WebSocket path.** WebSocket URLs are established connections, not stateless requests. Keep `/ws/events` as-is.

---

## Exit Criteria

- [ ] **All endpoints respond under `/api/v1/...`** (canonical path)
- [ ] **Legacy `/api/...` paths redirect** to `/api/v1/...` with `307`
- [ ] **Desktop app updated** to use `/api/v1/` base URL
- [ ] **`X-API-Version` header** present on all responses
- [ ] **All existing tests pass** (updated URLs where needed)
