# B-03 — Extract Shared State from `server.py`

**Owner:** Aryan
**Priority:** P0
**Status:** ⬜ Not Started
**Estimated effort:** 1–2 days
**Depends on:** Nothing (should start BEFORE B-01)
**Blocks:** B-01 (route modules need to import state from a proper class, not globals)

---

## Objective

Extract the global mutable variables in `server.py` (`_notifications`, `_activity_log`, `_watch_handles`, `_ws_clients`, `_last_verified`, `_connection_states`, `_dashboard_summary_cache`, etc.) into a proper `AppState` class with thread-safe access. After this task, zero global mutable state exists in `server.py` — all state is accessed through `request.app.state.app_state`.

---

## Why This Matters

- **Currently:** `server.py` has 10+ global mutable variables (lines 141–169) shared across all endpoints. This creates:
  - **Race conditions:** Multiple concurrent requests modify `_notifications` or `_ws_clients` without locks
  - **Testing difficulty:** Tests can't reset state between runs without monkeypatching globals
  - **Decomposition blocker:** Route modules can't import globals from `server.py` without creating circular imports
- **After:** One `AppState` object holds all runtime state with thread-safe access. Route modules receive it via dependency injection. Tests create fresh state per test.

---

## Current Global State Inventory

From `server.py` lines 141–169:

| Variable | Type | Purpose | Thread-Safe? |
|---|---|---|---|
| `_active_watches` | `Dict[str, WatchHandle]` | Active watcher handles | ❌ No |
| `_watch_metadata` | `Dict[str, Dict]` | Watcher metadata (connector, target, etc.) | ❌ No |
| `_paused_watches` | `Set[str]` | IDs of paused watchers | ❌ No |
| `_ws_clients` | `Set[WebSocket]` | Active WebSocket connections | ❌ No |
| `_ws_polling_task` | `Optional[asyncio.Task]` | Background polling task | ❌ No |
| `_notifications` | `List[Dict]` | In-memory notification store | ❌ No |
| `_activity_log` | `List[Dict]` | In-memory activity log | ❌ No |
| `_dashboard_summary_cache` | `Dict` | TTL cache for dashboard data | ❌ No |
| `_connection_states` | `Dict[str, Dict]` | Per-connector auth state cache | ❌ No |
| `_health_check_task` | `Optional[asyncio.Task]` | Background health check task | ❌ No |
| `_auth_environment_lock` | `threading.RLock` | Lock for env var projection | ✅ Yes (is a lock) |
| `_dotenv_lock` | `threading.RLock` | Lock for .env file access | ✅ Yes (is a lock) |

---

## Implementation Plan

### Step 1: Create `prash/state.py`

```python
"""Centralized application state.

All runtime mutable state lives here in one object. Route modules
and background tasks access it via `request.app.state.app_state`.
Tests create a fresh AppState() per test for isolation.
"""
from __future__ import annotations

import asyncio
import threading
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from fastapi import WebSocket
from prash.connectors.base import WatchHandle


class AppState:
    """Thread-safe container for all server runtime state."""

    def __init__(self) -> None:
        # -- Watcher State --
        self._lock = threading.RLock()
        self.active_watches: Dict[str, WatchHandle] = {}
        self.watch_metadata: Dict[str, Dict[str, Any]] = {}
        self.paused_watches: Set[str] = set()

        # -- WebSocket State --
        self.ws_clients: Set[WebSocket] = set()
        self.ws_polling_task: Optional[asyncio.Task] = None

        # -- Notification State --
        self.notifications: List[Dict[str, Any]] = []

        # -- Activity Log --
        self.activity_log: List[Dict[str, Any]] = []

        # -- Dashboard Cache --
        self.dashboard_cache: Dict[str, Any] = {
            "timestamp": 0.0,
            "data": None,
        }

        # -- Connection State --
        self.connection_states: Dict[str, Dict[str, Any]] = {}
        self.health_check_task: Optional[asyncio.Task] = None

        # -- Locks --
        self.auth_environment_lock = threading.RLock()
        self.dotenv_lock = threading.RLock()

    # -- Thread-safe notification access --
    def add_notification(self, notification: Dict[str, Any]) -> None:
        with self._lock:
            self.notifications.insert(0, notification)
            # Cap at 100
            if len(self.notifications) > 100:
                self.notifications = self.notifications[:100]

    def mark_notification_read(self, notification_id: str) -> bool:
        with self._lock:
            for n in self.notifications:
                if n.get("id") == notification_id:
                    n["read"] = True
                    return True
            return False

    def clear_notifications(self) -> None:
        with self._lock:
            self.notifications.clear()

    # -- Thread-safe activity log access --
    def add_activity(self, entry: Dict[str, Any]) -> None:
        with self._lock:
            self.activity_log.insert(0, entry)
            if len(self.activity_log) > 200:
                self.activity_log = self.activity_log[:200]

    # -- Thread-safe WebSocket client management --
    def add_ws_client(self, ws: WebSocket) -> None:
        with self._lock:
            self.ws_clients.add(ws)

    def remove_ws_client(self, ws: WebSocket) -> None:
        with self._lock:
            self.ws_clients.discard(ws)

    # -- Thread-safe watcher management --
    def add_watch(self, watch_id: str, handle: WatchHandle, metadata: Dict[str, Any]) -> None:
        with self._lock:
            self.active_watches[watch_id] = handle
            self.watch_metadata[watch_id] = metadata

    def remove_watch(self, watch_id: str) -> Optional[WatchHandle]:
        with self._lock:
            self.watch_metadata.pop(watch_id, None)
            self.paused_watches.discard(watch_id)
            return self.active_watches.pop(watch_id, None)

    # -- Startup / Shutdown --
    async def startup(self) -> None:
        """Called during app lifespan startup."""
        # Load persisted notifications, restore watches, start polling
        pass  # Will be filled during extraction

    async def shutdown(self) -> None:
        """Called during app lifespan shutdown."""
        # Cancel tasks, stop watches, cleanup
        if self.ws_polling_task:
            self.ws_polling_task.cancel()
        if self.health_check_task:
            self.health_check_task.cancel()
        for handle in list(self.active_watches.values()):
            try:
                handle.stop()
            except Exception:
                pass
        self.active_watches.clear()
        self.watch_metadata.clear()
        self.paused_watches.clear()
```

### Step 2: Create a dependency for route modules

```python
# prash/dependencies.py
"""FastAPI dependency functions for route modules."""
from __future__ import annotations

from fastapi import Request
from prash.state import AppState


def get_app_state(request: Request) -> AppState:
    """FastAPI dependency — returns the app-wide state object."""
    return request.app.state.app_state
```

### Step 3: Wire AppState into the app

In `server.py`:

```python
from prash.state import AppState

app.state.app_state = AppState()
```

### Step 4: Migrate endpoint handlers

Replace all global variable access with `AppState` method calls:

**Before:**
```python
@app.post("/api/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str):
    for n in _notifications:
        if n["id"] == notification_id:
            n["read"] = True
            _save_notifications_to_disk()
            return {"ok": True}
    raise HTTPException(status_code=404)
```

**After:**
```python
from fastapi import Depends
from prash.dependencies import get_app_state
from prash.state import AppState

@app.post("/api/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    state: AppState = Depends(get_app_state),
):
    if state.mark_notification_read(notification_id):
        _save_notifications_to_disk()  # Still reads from state.notifications
        return {"ok": True}
    raise HTTPException(status_code=404)
```

### Step 5: Write concurrency test

Create `tests/test_state_concurrency.py`:

```python
"""Verify AppState is thread-safe under concurrent access."""
import threading
from prash.state import AppState

def test_concurrent_notification_adds():
    state = AppState()
    errors = []

    def add_many(thread_id: int):
        try:
            for i in range(100):
                state.add_notification({"id": f"t{thread_id}-{i}", "msg": f"test"})
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=add_many, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors
    # 10 threads × 100 notifications, capped at 100
    assert len(state.notifications) == 100

def test_concurrent_ws_client_add_remove():
    state = AppState()
    # Test that add/remove under contention doesn't raise
    ...
```

---

## Checklist

### Preparation
- [ ] Catalog every global mutable variable in `server.py` (lines 141–169)
- [ ] For each variable, identify all read/write sites in the 3,896-line file
- [ ] Determine which operations need locking (writes to shared collections)

### Implementation
- [ ] Create `prash/state.py` with `AppState` class
- [ ] Add thread-safe methods for every state mutation (notifications, watchers, WS clients, activity log)
- [ ] Create `prash/dependencies.py` with `get_app_state()` dependency
- [ ] Wire `app.state.app_state = AppState()` in `server.py`
- [ ] Migrate ALL global variable reads/writes to use `AppState` methods
- [ ] Remove all global `_notifications`, `_activity_log`, etc. variables from `server.py`
- [ ] Move the `lifespan()` startup/shutdown logic into `AppState.startup()` / `AppState.shutdown()`

### Testing
- [ ] `tests/test_state_concurrency.py` — concurrent reads/writes don't crash
- [ ] Race condition test: 10 threads adding notifications simultaneously
- [ ] All existing tests pass (state is now injected, but behavior unchanged)
- [ ] Confirm zero global mutable state in `server.py`: `grep -n "^_" prash/server.py` shows only constants

---

## Anti-Patterns to Avoid

> **🚫 DO NOT use `asyncio.Lock` for everything.** Some state access happens from sync threads (watcher callbacks, connector SDK callbacks). Use `threading.RLock` which works in both sync and async contexts.

> **🚫 DO NOT make AppState a singleton.** Tests need fresh state per test. The app creates ONE AppState and assigns it to `app.state.app_state`. Tests create their own.

> **🚫 DO NOT hold locks while doing I/O.** Lock acquisition → mutate in-memory state → release lock. File I/O (`_save_notifications_to_disk`) happens AFTER the lock is released.

> **🚫 DO NOT use `@property` for mutable collections.** Returning `self.notifications` gives the caller a reference to the internal list — they can mutate it without the lock. Use methods that return copies or perform the mutation inside the lock.

> **🚫 DO NOT move business logic into AppState.** AppState is a state CONTAINER with thread-safe accessors. Business logic (formatting notifications, checking watcher health) stays in the route modules.

---

## Exit Criteria

- [ ] **Zero global mutable state in route modules** — `grep -rn "^_[a-z].*=.*\[\|{" prash/server.py` returns 0 hits (excluding constants and `_` private functions)
- [ ] **All state accessed through `request.app.state.app_state`** via the `get_app_state` dependency
- [ ] **Race condition test with concurrent requests passes** — `test_state_concurrency.py`
- [ ] **All existing tests pass** without modification
