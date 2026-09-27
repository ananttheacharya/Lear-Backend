# S-01 — Input Validation and Sanitization on All API Endpoints

**Owner:** Aryan
**Priority:** P0
**Status:** ⬜ Not Started
**Estimated effort:** 2–3 days
**Depends on:** Nothing (can start immediately)
**Blocks:** S-04 (credential expiry detection relies on validated endpoints)

---

## Objective

Audit every `Body()`, `Query()`, `Path()` parameter across all 83 endpoints in `prash/server.py` (165 KB / 3,896 lines). Replace all raw `dict` bodies and untyped parameters with Pydantic request models containing field validators. Malformed input must return a structured `422 Unprocessable Entity` response — never a raw `500 Internal Server Error`.

---

## Why This Matters

- **Currently:** Many endpoints accept `dict` or `Any` bodies with no validation. A malicious or malformed payload can trigger uncaught `KeyError`, `TypeError`, or `AttributeError` exceptions that leak stack traces and crash the endpoint.
- **After:** Every input is validated at the boundary. Invalid data is rejected with a clear, structured error before any business logic executes.

---

## Current State Audit

### Endpoints to audit (83 total in `server.py`)

**Connector routes (12 endpoints):**
- `GET /api/connectors` — query params
- `GET /api/connectors/{connector_id}` — path param
- `POST /api/connectors/{connector_id}/connect` — **body: credentials dict** ← highest risk
- `POST /api/connectors/{connector_id}/disconnect` — path param
- `DELETE /api/connectors/{connector_id}/disconnect` — path param
- `POST /api/connectors/{connector_id}/check` — body
- `GET /api/connectors/{connector_id}/validate` — path param
- `GET /api/connectors/{connector_id}/status` — path param
- `GET /api/connectors/{connector_id}/metrics` — path + query params
- `GET /api/connectors/{connector_id}/resources` — path param
- `POST /api/connectors/{connector_id}/watch` — **body: target + interval** ← needs validation
- `DELETE /api/connectors/{connector_id}/watch` — path param

**Watcher routes (4 endpoints):**
- `POST /api/connectors/{connector_id}/watch/pause`
- `POST /api/connectors/{connector_id}/watch/resume`
- `GET /api/watch/poll`
- `GET /api/watch/active`

**Dashboard routes (2 endpoints):**
- `GET /api/dashboard/summary`
- `GET /api/dashboard/activity`

**Chat routes (8 endpoints):**
- `GET /api/chat/greeting`
- `POST /api/chat` — **body: message payload** ← needs validation
- `POST /api/chat/stream` — **body: message payload** ← needs validation
- `POST /api/chat/execute` — **body: action execution** ← highest risk
- `GET /api/chat/sessions`
- `GET /api/chat/sessions/{session_id}`
- `POST /api/chat/sessions`
- `POST /api/chat/sessions/{session_id}/message` — **body**

**Project routes (5 endpoints):**
- `GET /api/projects`
- `POST /api/projects` — **body: project config** ← needs validation
- `PUT /api/projects/{project_id}` — **body: project update** ← needs validation
- `GET /api/projects/{project_id}/status`
- `DELETE /api/projects/{project_id}`

**Settings/config routes (4 endpoints):**
- `GET /api/config`
- `POST /api/config` — **body: config update**
- `GET /api/settings`
- `POST /api/settings` — **body: settings update**

**Widget routes (4 endpoints):**
- `POST /api/connectors/{connector_id}/generate-widgets` — **body**
- `GET /api/connectors/{connector_id}/widgets`
- `PUT /api/connectors/{connector_id}/widgets` — **body: widget layout**
- `DELETE /api/connectors/{connector_id}/widgets`

**Notification routes (3 endpoints):**
- `GET /api/notifications`
- `POST /api/notifications/{notification_id}/read`
- `DELETE /api/notifications`

**Other routes:** system/version, status, demo endpoints, incident endpoints, upload, email/slack

---

## Implementation Plan

### Step 1: Create the request models module

Create `prash/api_models.py` — a single file containing ALL Pydantic request/response models.

```python
# prash/api_models.py
from __future__ import annotations
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Any, Dict, List, Optional
import re

# ── Connector Models ──────────────────────────────────────────────
class ConnectorConnectRequest(BaseModel):
    """Body for POST /api/connectors/{connector_id}/connect"""
    credentials: Dict[str, str] = Field(
        ..., description="Key-value pairs for connector auth fields"
    )

    @field_validator("credentials")
    @classmethod
    def credentials_not_empty(cls, v: Dict[str, str]) -> Dict[str, str]:
        if not v:
            raise ValueError("credentials dict must not be empty")
        # Strip whitespace from values, reject if all-whitespace
        cleaned = {}
        for key, val in v.items():
            if not isinstance(key, str) or not key.strip():
                raise ValueError(f"credential key must be a non-empty string")
            if not isinstance(val, str):
                raise ValueError(f"credential value for '{key}' must be a string")
            cleaned[key.strip()] = val.strip()
        return cleaned

class WatchStartRequest(BaseModel):
    """Body for POST /api/connectors/{connector_id}/watch"""
    target: str = Field(..., min_length=1, max_length=500)
    interval: int = Field(default=30, ge=5, le=3600)

    @field_validator("target")
    @classmethod
    def sanitize_target(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("target must not be blank")
        return v

# ... (continue for all endpoint bodies)
```

### Step 2: Add validators to path parameters

Every `{connector_id}` path parameter must be validated:

```python
from fastapi import Path

@app.get("/api/connectors/{connector_id}")
async def get_connector_detail(
    connector_id: str = Path(
        ...,
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9_-]+$",
        description="Connector identifier from CONNECTOR_REGISTRY"
    )
):
    ...
```

### Step 3: Replace raw dict bodies endpoint-by-endpoint

For each endpoint that currently accepts `body: dict = Body(...)`:

1. Identify the expected shape by reading the endpoint implementation
2. Create a Pydantic model in `api_models.py`
3. Replace the `dict` param with the typed model
4. Run the endpoint's existing tests — they must pass unchanged
5. Add a malformed-input test

### Step 4: Add fuzz testing

Create `tests/test_input_validation.py`:

```python
"""Fuzz 50 malformed payloads against every POST/PUT endpoint.
None of them should produce a 500 — only 400/422."""

import pytest
from fastapi.testclient import TestClient

MALFORMED_PAYLOADS = [
    None,                           # null body
    "",                             # empty string
    42,                             # wrong type
    [],                             # array instead of object
    {"<script>alert(1)</script>": "xss"},  # XSS in key
    {"key": "<script>alert(1)</script>"},  # XSS in value
    {"key": "a" * 100_000},         # oversized value
    {"key": "\x00\x01\x02"},        # null bytes
    {"credentials": {}},            # empty nested dict
    {"credentials": None},          # null nested
    {"target": ""},                 # empty required field
    {"target": " "},                # whitespace-only
    {"interval": -1},               # negative number
    {"interval": 999999},           # out of range
    {"interval": "not_a_number"},   # wrong type
    # ... build up to 50+
]

WRITE_ENDPOINTS = [
    ("POST", "/api/connectors/github/connect"),
    ("POST", "/api/chat"),
    ("POST", "/api/chat/stream"),
    ("POST", "/api/chat/execute"),
    ("POST", "/api/projects"),
    ("POST", "/api/config"),
    ("POST", "/api/settings"),
    # ... all POST/PUT endpoints
]

@pytest.mark.parametrize("payload", MALFORMED_PAYLOADS)
@pytest.mark.parametrize("method,path", WRITE_ENDPOINTS)
def test_no_500_on_malformed_input(client, method, path, payload):
    resp = getattr(client, method.lower())(path, json=payload)
    assert resp.status_code != 500, (
        f"{method} {path} returned 500 on payload: {payload!r}"
    )
```

---

## Checklist

### Preparation
- [ ] Read every endpoint in `server.py` (lines 397–3896) and catalog which accept bodies
- [ ] Cross-reference with `test_desktop_api.py` (46 KB) to see which endpoints already have tests
- [ ] List every `Body()`, `Query()`, `Path()` parameter and its current type

### Implementation
- [ ] Create `prash/api_models.py` with Pydantic models for every request body
- [ ] Add `field_validator` for any field that needs sanitization (strip whitespace, reject nulls, length limits)
- [ ] Add `Path()` constraints to every `{connector_id}`, `{project_id}`, `{session_id}`, `{notification_id}`, `{incident_id}` path param
- [ ] Add `Query()` constraints to query parameters with defaults and type bounds
- [ ] Replace each raw `dict` body with its typed Pydantic model
- [ ] Confirm every endpoint returns `422` for invalid input (FastAPI does this automatically with Pydantic models)
- [ ] Confirm no endpoint returns `500` for malformed input

### Testing
- [ ] All existing tests in `test_desktop_api.py` pass without modification
- [ ] All existing tests in other test files pass without modification
- [ ] New `tests/test_input_validation.py` with 50+ malformed payloads — 0 crashes (no 500s)
- [ ] Each new Pydantic model has at least one unit test for its validators

### Documentation
- [ ] PR description lists every endpoint that was changed
- [ ] `api_models.py` has docstrings on every model explaining which endpoint it serves

---

## Anti-Patterns to Avoid

> **🚫 DO NOT hardcode connector IDs in validators.** Use `CONNECTOR_REGISTRY.keys()` dynamically.

> **🚫 DO NOT change endpoint behavior.** This task is ONLY about input validation. If an endpoint currently accepts `{"foo": "bar"}` and works, the Pydantic model must accept the same shape. Do not rename fields.

> **🚫 DO NOT add response models yet.** Response typing is a separate concern (tracked separately). This task is request-side only.

> **🚫 DO NOT add auth/permission checks in this task.** That's S-07 and the existing permissions system.

> **🚫 DO NOT use `model_config = {"extra": "forbid"}` globally.** Some endpoints intentionally accept extra fields (e.g., connector credentials are dynamic per connector). Use `extra = "forbid"` only where the schema is fully known and fixed.

> **🚫 DO NOT suppress Pydantic's default 422 error format.** Let FastAPI's built-in validation error handler return the standard `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}` structure. Clients already handle this.

---

## Exit Criteria

- [ ] **Every endpoint has a typed Pydantic request model** (for those that accept bodies) or constrained `Path()`/`Query()` parameters
- [ ] **Zero raw `dict` bodies accepted** — grep for `Body(...)` with no type annotation returns 0 hits
- [ ] **Fuzz test with 50 malformed payloads — 0 crashes** — `test_input_validation.py` passes, no 500s
- [ ] **All 800+ existing tests pass** without modification
