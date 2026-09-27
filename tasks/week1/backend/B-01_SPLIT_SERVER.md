# B-01 — Split `server.py` into Route Modules

**Owner:** Aryan
**Priority:** P0
**Status:** ⬜ Not Started
**Estimated effort:** 2–3 days
**Depends on:** B-03 (extract shared state first — route modules should import from `AppState`, not use globals)
**Blocks:** B-04 (API versioning needs route modules to exist), S-02 (rate limiting is easier with routers)

---

## Objective

Decompose the 3,896-line `prash/server.py` monolith into focused route modules using FastAPI's `APIRouter`. After this task, `server.py` is the app factory only (under 200 lines), and all endpoint logic lives in `prash/routes/*.py`.

---

## Why This Matters

- **Currently:** `server.py` is 165 KB / 3,896 lines containing 83 endpoint handlers, global state, helper functions, middleware, lifespan management, and business logic all in one file. This makes it:
  - Impossible to review PRs that touch the file (merge conflicts guaranteed)
  - Difficult to test individual route groups in isolation
  - Hard to navigate (finding a specific endpoint requires searching 4K lines)
- **After:** Each route group is a self-contained module. Endpoints are organized by domain. `server.py` is a thin app factory that registers routers and middleware.

---

## Route Module Breakdown

Based on the 83 endpoints currently in `server.py`, split into these modules:

| Module | Endpoints | Approximate Lines |
|---|---|---|
| `routes/connectors.py` | `/api/connectors`, `/api/connectors/{id}/*`, `/api/connect/{id}` | ~600 |
| `routes/watcher.py` | `/api/connectors/{id}/watch`, `/api/watch/*`, WebSocket `/ws/events` | ~400 |
| `routes/chat.py` | `/api/chat/*`, `/api/chat/sessions/*`, `/api/chat/upload` | ~500 |
| `routes/dashboard.py` | `/api/dashboard/*`, `/api/status`, `/api/metrics/*` | ~300 |
| `routes/settings.py` | `/api/settings`, `/api/config` | ~150 |
| `routes/notifications.py` | `/api/notifications/*` | ~100 |
| `routes/projects.py` | `/api/projects/*` | ~300 |
| `routes/widgets.py` | `/api/connectors/{id}/widgets`, `/api/connectors/{id}/generate-widgets` | ~200 |
| `routes/activity.py` | `/api/activity` | ~50 |
| `routes/system.py` | `/api/system/*`, `/api/auth/*` | ~50 |
| `routes/demo.py` | `/demo`, `/store`, `/admin`, `/api/demo/*` | ~800 |
| `routes/incidents.py` | `/incident/*`, `/api/incident/*`, `/api/incidents` | ~400 |
| `routes/email.py` | `/api/email/*` | ~100 |
| `routes/slack.py` | `/api/slack/*` | ~100 |

---

## Implementation Plan

### Step 1: Create the `routes/` package

```
prash/
  routes/
    __init__.py          # Empty or router registration helper
    connectors.py
    watcher.py
    chat.py
    dashboard.py
    settings.py
    notifications.py
    projects.py
    widgets.py
    activity.py
    system.py
    demo.py
    incidents.py
    email.py
    slack.py
```

### Step 2: Extract one module at a time (NOT all at once)

The safest approach is to extract one route group, run all tests, commit, then move to the next.

**Order of extraction** (easiest/least-coupled first):

1. `routes/system.py` — `/api/system/version` (small, no dependencies)
2. `routes/activity.py` — `/api/activity` (small, reads from `_activity_log`)
3. `routes/notifications.py` — `/api/notifications/*` (isolated)
4. `routes/settings.py` — `/api/settings`, `/api/config` (reads/writes `.env`)
5. `routes/projects.py` — `/api/projects/*` (reads/writes `prash.yaml`)
6. `routes/widgets.py` — widget-related endpoints
7. `routes/dashboard.py` — dashboard summary + activity
8. `routes/connectors.py` — **largest group, most coupling to shared state**
9. `routes/watcher.py` — watcher management + WebSocket
10. `routes/chat.py` — chat/streaming endpoints
11. `routes/demo.py` — demo/store/admin pages
12. `routes/incidents.py` — incident management
13. `routes/email.py` — email endpoints
14. `routes/slack.py` — Slack endpoints

### Step 3: Pattern for each extraction

Each route module follows this exact pattern:

```python
# prash/routes/system.py
"""System information and health endpoints."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["system"])


@router.get("/system/version")
async def get_system_version():
    """Return system version and configuration info."""
    return {
        "name": "Lear",
        "version": "2.0.0",
        "engine": "FastAPI + Prash Core",
        # ... rest of the existing implementation
    }
```

### Step 4: Register routers in `server.py`

After all extractions, `server.py` becomes:

```python
"""Lear Backend — FastAPI Application Factory.

This file creates the FastAPI app, registers middleware, and mounts
route modules. All endpoint logic lives in prash/routes/*.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from prash.routes import (
    activity, chat, connectors, dashboard, demo, email,
    incidents, notifications, projects, settings, slack,
    system, watcher, widgets,
)
from prash.state import AppState


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic (restore watches, start polling, etc.)
    state: AppState = app.state.app_state
    await state.startup()
    yield
    await state.shutdown()


def create_app() -> FastAPI:
    app = FastAPI(title="Lear Desktop API", version="2.0.0", lifespan=lifespan)

    # -- State --
    app.state.app_state = AppState()

    # -- Middleware --
    app.add_middleware(CORSMiddleware, ...)

    # -- Routers --
    app.include_router(system.router)
    app.include_router(connectors.router)
    app.include_router(watcher.router)
    app.include_router(chat.router)
    app.include_router(dashboard.router)
    app.include_router(settings.router)
    app.include_router(notifications.router)
    app.include_router(projects.router)
    app.include_router(widgets.router)
    app.include_router(activity.router)
    app.include_router(demo.router)
    app.include_router(incidents.router)
    app.include_router(email.router)
    app.include_router(slack.router)

    return app


app = create_app()
```

### Step 5: Verify after each extraction

After extracting each module:

```bash
# Run ALL tests — not just the ones you think are related
pytest tests/ -x -q

# Verify endpoint count hasn't changed
python -c "
from prash.server import app
routes = [r for r in app.routes if hasattr(r, 'methods')]
print(f'Endpoints: {len(routes)}')
"

# Verify specific endpoint paths haven't changed
curl http://localhost:8000/api/system/version
```

---

## Checklist

### Preparation
- [ ] Read all 3,896 lines of `server.py` and map each endpoint to its target module
- [ ] Ensure B-03 (shared state extraction) is complete — route modules need `AppState`
- [ ] Create `prash/routes/__init__.py`

### Extraction (one at a time, test between each)
- [ ] Extract `routes/system.py` → run tests → commit
- [ ] Extract `routes/activity.py` → run tests → commit
- [ ] Extract `routes/notifications.py` → run tests → commit
- [ ] Extract `routes/settings.py` → run tests → commit
- [ ] Extract `routes/projects.py` → run tests → commit
- [ ] Extract `routes/widgets.py` → run tests → commit
- [ ] Extract `routes/dashboard.py` → run tests → commit
- [ ] Extract `routes/connectors.py` → run tests → commit
- [ ] Extract `routes/watcher.py` → run tests → commit
- [ ] Extract `routes/chat.py` → run tests → commit
- [ ] Extract `routes/demo.py` → run tests → commit
- [ ] Extract `routes/incidents.py` → run tests → commit
- [ ] Extract `routes/email.py` → run tests → commit
- [ ] Extract `routes/slack.py` → run tests → commit

### Final Verification
- [ ] `server.py` is under 200 lines
- [ ] Each route module is a `FastAPI.APIRouter`
- [ ] All 83 endpoints still respond at the same paths
- [ ] All existing tests pass without modification
- [ ] Zero endpoint behavior changes (same request → same response)
- [ ] `wc -l prash/server.py` < 200

---

## Anti-Patterns to Avoid

> **🚫 DO NOT change endpoint paths or behavior.** This is a pure structural refactor. Every endpoint must respond at the exact same URL with the exact same request/response contract. If tests break, the extraction was wrong — don't "fix" the tests.

> **🚫 DO NOT extract all modules in one mega-commit.** Extract one at a time, test, commit. This makes bisecting trivial if something breaks.

> **🚫 DO NOT import app-level state directly in route modules.** Route modules should receive state through dependency injection (`request.app.state.app_state`) or FastAPI's `Depends()`. See B-03.

> **🚫 DO NOT duplicate helper functions.** If a helper function is used by multiple route modules, put it in a shared module (e.g., `prash/routes/_helpers.py` or `prash/utils.py`). Don't copy-paste.

> **🚫 DO NOT move the exception handlers into route modules.** Exception handlers are app-level concerns — they stay in `server.py` or a dedicated `prash/error_handlers.py`.

> **🚫 DO NOT add `prefix="/api"` to the router AND keep `/api/` in the route decorators.** That doubles the prefix. Either the router has the prefix, or the individual routes do — not both.

---

## Exit Criteria

- [ ] **`server.py` under 200 lines** — app factory only
- [ ] **Each route module is a `FastAPI.APIRouter`** with appropriate `prefix` and `tags`
- [ ] **All existing tests pass without modification** — `pytest tests/ -x` green
- [ ] **Zero endpoint behavior changes** — same paths, same contracts
- [ ] **All 83 endpoints still respond** — verified by running the test suite
