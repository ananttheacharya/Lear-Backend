# T-02 — Add Missing Integration Tests for `server.py` Endpoint Contracts

**Owner:** Anant
**Priority:** P1
**Status:** ⬜ Not Started
**Estimated effort:** 2–3 days
**Depends on:** T-01 (need coverage baseline to know what's missing)
**Blocks:** Nothing

---

## Objective

Every endpoint in `server.py` must have at least one happy-path test and one error-path test. Cross-reference the existing `test_desktop_api.py` (46 KB) to identify gaps. Target: coverage for server routes at or above 70%.

---

## Why This Matters

- **Currently:** `test_desktop_api.py` (46 KB) has substantial coverage, but some endpoints may only have happy-path tests and no error-path tests. Some newer endpoints (incidents, email, slack) may have no tests at all.
- **After:** Every endpoint has verified contracts — we know exactly what request produces what response, for both success and failure cases. This prevents regressions when B-01 (route splitting) moves code around.

---

## Current Test State

Existing test files relevant to server endpoints:

| File | Size | What it covers |
|---|---|---|
| `test_desktop_api.py` | 46 KB | Most `/api/connectors/*`, `/api/dashboard/*`, `/api/chat/*`, etc. |
| `test_service_connections.py` | 15 KB | Connector connect/disconnect flow |
| `test_watcher.py` | 44 KB | Watcher start/stop/poll |
| `test_notifications.py` | 6.5 KB | Notification CRUD |
| `test_widget_generation.py` | 6.4 KB | Widget generation/save/load |

---

## Implementation Plan

### Step 1: Map existing test coverage

Create a coverage matrix — every endpoint vs. its test status:

```
Endpoint                                    | Happy Path | Error Path | Test File
--------------------------------------------|------------|------------|----------
GET  /api/connectors                        |     ✅     |     ?      | test_desktop_api.py
GET  /api/connectors/{id}                   |     ✅     |     ?      | test_desktop_api.py
POST /api/connectors/{id}/connect           |     ✅     |     ?      | test_service_connections.py
POST /api/connectors/{id}/disconnect        |     ✅     |     ?      | test_service_connections.py
DELETE /api/connectors/{id}/disconnect      |     ?      |     ?      |
POST /api/connectors/{id}/check             |     ?      |     ?      |
GET  /api/connectors/{id}/validate          |     ✅     |     ?      | test_service_connections.py
...
POST /api/chat                              |     ✅     |     ?      | test_desktop_api.py
POST /api/chat/stream                       |     ?      |     ?      |
POST /api/chat/execute                      |     ?      |     ?      |
...
GET  /api/incidents                          |     ?      |     ?      |
POST /api/slack/chat                         |     ?      |     ?      |
POST /api/email/chat                         |     ?      |     ?      |
```

Fill in every cell. The `?` marks are the gaps to fill.

### Step 2: Write tests for each gap

For each untested endpoint, write:

**Happy-path test:** Send a valid request, verify the response status code and structure.

```python
def test_get_connectors_returns_list(client):
    """GET /api/connectors returns a list of connector details."""
    resp = client.get("/api/connectors")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Verify structure of first item
    item = data[0]
    assert "id" in item
    assert "name" in item
    assert "category" in item
```

**Error-path test:** Send an invalid request, verify the error response.

```python
def test_get_connector_invalid_id_returns_404(client):
    """GET /api/connectors/{id} with nonexistent ID returns 404."""
    resp = client.get("/api/connectors/nonexistent_connector_12345")
    assert resp.status_code == 404

def test_connect_connector_missing_body_returns_422(client):
    """POST /api/connectors/{id}/connect without body returns 422."""
    resp = client.post("/api/connectors/github/connect")
    assert resp.status_code == 422
```

### Step 3: Test categories to focus on

**Highest priority (these touch external systems):**
- `POST /api/connectors/{id}/connect` — credential submission
- `POST /api/chat/execute` — action execution
- `POST /api/chat/stream` — LLM streaming
- `POST /api/connectors/{id}/watch` — watcher creation

**Medium priority (data management):**
- `POST /api/projects` — project creation
- `PUT /api/projects/{id}` — project update
- `POST /api/settings` — settings update
- `POST /api/config` — config update

**Lower priority (read-only / demo):**
- `GET /api/dashboard/summary`
- `GET /api/demo/*`
- `GET /api/incidents`

### Step 4: Error scenarios to cover

For each write endpoint, test at minimum:

| Scenario | Expected Status |
|---|---|
| Missing request body | 422 |
| Wrong body type (string instead of object) | 422 |
| Missing required field | 422 |
| Invalid path parameter | 404 |
| Non-existent resource | 404 |
| Invalid field value (e.g., negative interval) | 400 or 422 |

### Step 5: Organization

Add tests to the existing `test_desktop_api.py` or create per-domain test files:

```
tests/
  test_desktop_api.py              # Existing — keep, add gaps
  test_endpoint_contracts.py       # NEW — focused on contract verification
  test_endpoint_errors.py          # NEW — focused on error paths
```

Or extend the existing file — consistency with the current codebase matters more than a new structure.

---

## Checklist

### Gap Analysis
- [ ] Create the coverage matrix (all 83 endpoints × happy/error test status)
- [ ] Cross-reference with `test_desktop_api.py` to mark existing coverage
- [ ] Cross-reference with other test files (`test_watcher.py`, `test_notifications.py`, etc.)
- [ ] Identify every endpoint with missing happy-path test
- [ ] Identify every endpoint with missing error-path test

### Test Writing
- [ ] For each gap, write at least one happy-path test (valid request → expected response)
- [ ] For each gap, write at least one error-path test (invalid request → proper error)
- [ ] For write endpoints: test missing body, wrong type, missing required fields
- [ ] For read endpoints: test invalid path params, non-existent resources
- [ ] For connector endpoints: test with unconfigured connector
- [ ] For chat endpoints: test with invalid/empty message

### Verification
- [ ] All new tests pass: `pytest tests/test_endpoint_contracts.py -x -q`
- [ ] All existing tests still pass: `pytest tests/ -x -q`
- [ ] Coverage for server routes at or above 70% (re-run T-01 measurement)
- [ ] Every REST endpoint has 2+ tests (happy + error)

---

## Anti-Patterns to Avoid

> **🚫 DO NOT test implementation details.** Test the HTTP contract (request in → response out), not internal function calls. If the endpoint returns `{"status": "ok"}`, assert that — don't mock internal methods and assert they were called.

> **🚫 DO NOT make tests depend on external services.** All connector calls should be mocked. Tests must pass without network access, without API keys, without a running Kubernetes cluster.

> **🚫 DO NOT write tests that depend on other tests.** Each test must be independent. Use fixtures for setup, not "run test_A before test_B."

> **🚫 DO NOT duplicate existing tests.** If `test_desktop_api.py` already tests `GET /api/connectors`, don't write another test for it. Add the missing error-path test only.

> **🚫 DO NOT target 100% coverage.** The goal is 70% on server routes. Some code paths (edge cases in demo endpoints, error handling for rare failures) are not worth testing in this pass. Focus on the business-critical endpoints.

---

## Exit Criteria

- [ ] **Every REST endpoint has 2+ tests** (at least one happy-path + one error-path)
- [ ] **Coverage for `server.py` routes at or above 70%** (measured with `pytest --cov`)
- [ ] **All tests pass** — both new and existing
- [ ] **Coverage matrix documented** — shows which endpoints are tested where
