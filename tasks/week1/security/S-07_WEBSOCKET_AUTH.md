# S-07 — WebSocket Authentication

**Owner:** Aryan
**Priority:** P1
**Status:** ⬜ Not Started
**Estimated effort:** 1–2 days
**Depends on:** Nothing
**Blocks:** Nothing

---

## Objective

Add authentication to the `/ws/events` WebSocket endpoint. Currently it accepts ANY connection with no auth check. Implement a token-based handshake so only authorized clients can subscribe to the live event stream.

---

## Why This Matters

- **Currently:** `server.py` has a WebSocket endpoint at `/ws/events` (line ~397 area) with zero authentication. Anyone who can reach the server on the network can open a WebSocket and receive all live watcher events, notifications, and system state updates.
- **After:** WebSocket connections require a valid token. Unauthenticated connections are rejected with close code `4001`. The desktop app passes the token automatically.

---

## Current State

```python
# server.py — current WebSocket handler (no auth)
@app.websocket("/ws/events")
async def websocket_events(ws: WebSocket):
    await ws.accept()
    _ws_clients.add(ws)
    try:
        while True:
            await ws.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        _ws_clients.discard(ws)
```

The desktop app connects via `useWatcher.ts` hook — no token is sent.

---

## Implementation Plan

### Approach: Query Parameter Token

WebSocket connections don't support custom headers in the browser API, so the standard pattern is to pass the auth token as a query parameter:

```
ws://localhost:8000/ws/events?token=<jwt-or-shared-secret>
```

### Step 1: Define the auth mechanism

For a local-first desktop app, a **shared secret** is simpler and more appropriate than full JWT infrastructure:

```python
# prash/middleware/ws_auth.py
"""WebSocket authentication.

For the local-first Lear desktop app, we use a shared secret generated
at server startup and passed to the desktop app via the startup handshake.
This prevents unauthorized network access to the live event stream.
"""
from __future__ import annotations

import os
import secrets
from typing import Optional

# Generate a per-session token at server startup
# Can be overridden via env var for testing
_WS_TOKEN: Optional[str] = None


def get_ws_token() -> str:
    """Get or generate the WebSocket auth token."""
    global _WS_TOKEN
    if _WS_TOKEN is None:
        _WS_TOKEN = os.getenv("LEAR_WS_TOKEN", secrets.token_urlsafe(32))
    return _WS_TOKEN


def validate_ws_token(token: Optional[str]) -> bool:
    """Validate a WebSocket auth token."""
    if not token:
        return False
    return secrets.compare_digest(token, get_ws_token())
```

### Step 2: Update the WebSocket endpoint

```python
from prash.middleware.ws_auth import validate_ws_token, get_ws_token

@app.websocket("/ws/events")
async def websocket_events(ws: WebSocket, token: str = Query(default="")):
    # Validate token before accepting the connection
    if not validate_ws_token(token):
        await ws.close(code=4001, reason="Authentication required")
        return

    await ws.accept()
    _ws_clients.add(ws)
    try:
        while True:
            data = await ws.receive_text()
            # Optionally handle client messages here
    except WebSocketDisconnect:
        _ws_clients.discard(ws)
```

**Close code `4001`** — standard for application-level auth failure (4000–4999 are reserved for application use).

### Step 3: Expose the token to the desktop app

Add the token to the existing `/api/system/version` or a new `/api/auth/ws-token` endpoint:

```python
@app.get("/api/auth/ws-token")
async def get_websocket_token():
    """Return the WebSocket auth token for this session.

    This endpoint itself should be protected in production (future work).
    For now, it's accessible to any local client — matching the existing
    trust model of the desktop app.
    """
    return {"token": get_ws_token()}
```

### Step 4: Update the desktop app

In `desktop/src/hooks/useWatcher.ts` (or wherever the WebSocket is created):

```typescript
// Fetch the WS token, then connect
const fetchWsToken = async (): Promise<string> => {
  const resp = await fetch(`${API_BASE}/api/auth/ws-token`);
  const data = await resp.json();
  return data.token;
};

const connectWebSocket = async () => {
  const token = await fetchWsToken();
  const ws = new WebSocket(`ws://localhost:8000/ws/events?token=${token}`);
  // ... existing connection handling
};
```

### Step 5: Write tests

Create `tests/test_ws_auth.py`:

```python
"""WebSocket authentication tests."""
import pytest
from fastapi.testclient import TestClient

def test_ws_connect_without_token_rejected(client):
    """Unauthenticated WebSocket connection is rejected with 4001."""
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/events") as ws:
            # Should not reach here — connection should be rejected
            pass

def test_ws_connect_with_invalid_token_rejected(client):
    """WebSocket connection with wrong token is rejected."""
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/events?token=invalid-token") as ws:
            pass

def test_ws_connect_with_valid_token_succeeds(client):
    """WebSocket connection with valid token is accepted."""
    # Get the token
    resp = client.get("/api/auth/ws-token")
    token = resp.json()["token"]

    with client.websocket_connect(f"/ws/events?token={token}") as ws:
        # Connection succeeded — send a ping to verify it's alive
        ws.send_text("ping")
        # Connection should stay open (no immediate disconnect)

def test_ws_token_endpoint_returns_consistent_token(client):
    """Multiple calls to /api/auth/ws-token return the same token (per session)."""
    resp1 = client.get("/api/auth/ws-token")
    resp2 = client.get("/api/auth/ws-token")
    assert resp1.json()["token"] == resp2.json()["token"]
```

---

## Checklist

### Implementation
- [ ] Create `prash/middleware/ws_auth.py` with token generation and validation
- [ ] Update `/ws/events` handler to check token query parameter
- [ ] Reject unauthenticated connections with close code `4001`
- [ ] Create `/api/auth/ws-token` endpoint to expose the session token
- [ ] Use `secrets.compare_digest()` for timing-safe token comparison
- [ ] Token is per-session (generated at server startup, stable for the session lifetime)
- [ ] `LEAR_WS_TOKEN` env var allows override for testing

### Desktop App
- [ ] Update WebSocket connection code to fetch and use the token
- [ ] Handle token fetch failure gracefully (retry, show error)
- [ ] Handle `4001` close code specifically (re-fetch token and retry)

### Testing
- [ ] Test: unauthenticated connection → rejected with 4001
- [ ] Test: invalid token → rejected with 4001
- [ ] Test: valid token → connection accepted
- [ ] Test: token endpoint returns consistent token per session
- [ ] All existing WebSocket tests updated to use token
- [ ] All other existing tests pass

---

## Anti-Patterns to Avoid

> **🚫 DO NOT use JWT for this.** JWT is overkill for a single-user local-first app with no user accounts. A per-session shared secret is simpler, has fewer failure modes, and doesn't need key management. JWT can be added later if multi-user auth is needed.

> **🚫 DO NOT log the WebSocket token.** It's a secret. Log that a token was generated, but not the token value.

> **🚫 DO NOT put the token in a WebSocket subprotocol header.** While technically possible, it's non-standard and breaks some proxy/load balancer configurations. Query parameter is the established pattern.

> **🚫 DO NOT make the token endpoint require its own auth** (chicken-and-egg). The existing trust model is "any local client can access the API." The WS token prevents unauthorized *network* access, not local access. True auth is a separate, larger initiative.

> **🚫 DO NOT break existing WebSocket functionality.** The token is the only change. All event broadcasting, watch updates, and notification delivery via WebSocket must continue working exactly as before — just with the token handshake added.

---

## Exit Criteria

- [ ] **Unauthenticated WebSocket connection is rejected with close code `4001`**
- [ ] **Authenticated connection (valid token) proceeds normally**
- [ ] **Desktop app updated to fetch and use the token**
- [ ] **Tests prove both paths** — rejection and acceptance
- [ ] **All existing functionality (watchers, notifications, live events) works** through the authenticated WebSocket
- [ ] **All existing tests pass**
