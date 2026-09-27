# S-04 — Credential Rotation and Expiry Detection

**Owner:** Aryan
**Priority:** P1
**Status:** ⬜ Not Started
**Estimated effort:** 2 days
**Depends on:** S-01 (validated endpoints)
**Blocks:** Nothing

---

## Objective

Add TTL tracking to connector credentials. The backend detects when credentials are close to expiry (where the provider supports it) and exposes this via the existing `/api/connectors/{id}/validate` endpoint. The desktop `ConnectorForm` shows amber warnings when credentials are within 7 days of expiry.

---

## Why This Matters

- **Currently:** Credentials are stored in `.env` with no expiry tracking. When a GitHub PAT or AWS STS session token expires, the connector silently starts failing. The user discovers the problem only when they notice watchers stopped or a `prash fix` fails.
- **After:** The system proactively warns the user before credentials expire. At least AWS and GitHub connectors report credential age/expiry status.

---

## Connectors with Detectable Expiry

| Connector | Credential Type | Expiry Detection Method |
|---|---|---|
| **AWS** | STS session token, IAM access keys | `sts.get_session_token()` returns `Expiration`. IAM key age via `iam.list_access_keys()` → `CreateDate` |
| **GitHub** | PAT (classic or fine-grained) | GitHub API: `GET /user` — response includes `X-OAuth-Scopes`. Fine-grained PATs: `GET /` includes `github-authentication-token-expiration` header |
| **GitLab** | PAT | GitLab API: `GET /personal_access_tokens/self` returns `expires_at` |
| **Datadog** | API key + App key | No expiry (API keys don't expire). Skip this connector. |
| **PagerDuty** | API token | No standard expiry. Skip. |
| **Grafana** | API key / Service account token | Grafana API: service account tokens have `expiration` field |

**Phase 1 scope:** AWS + GitHub only (the two most commonly rotated credential types).

---

## Implementation Plan

### Step 1: Add credential metadata storage

Create `prash/credential_metadata.py`:

```python
"""Track credential age, expiry, and last-validated timestamps.

Stored in .prash/credential_meta.json alongside the existing .prash/ directory.
This is metadata ABOUT credentials, not the credentials themselves.
"""
from __future__ import annotations
import json
import os
import time
from dataclasses import dataclass, asdict
from typing import Optional

META_PATH = os.path.join(os.path.dirname(__file__), "..", ".prash", "credential_meta.json")

@dataclass
class CredentialMeta:
    connector_id: str
    last_validated: float          # Unix timestamp of last successful validate
    expires_at: Optional[float]    # Unix timestamp of credential expiry (None = unknown/never)
    created_at: Optional[float]    # Unix timestamp of when credential was first stored
    source: str                    # How expiry was determined: "provider_api", "manual", "unknown"

    @property
    def days_until_expiry(self) -> Optional[float]:
        if self.expires_at is None:
            return None
        return (self.expires_at - time.time()) / 86400

    @property
    def is_expiring_soon(self) -> bool:
        """True if expiry is within 7 days."""
        days = self.days_until_expiry
        return days is not None and days < 7

    @property
    def is_expired(self) -> bool:
        days = self.days_until_expiry
        return days is not None and days < 0


def load_all_meta() -> dict[str, CredentialMeta]:
    ...

def save_meta(connector_id: str, meta: CredentialMeta) -> None:
    ...
```

### Step 2: Add expiry detection to connectors

Add a `detect_credential_expiry()` method to the connectors that support it:

**AWS connector** (`connectors/aws.py`):
```python
def detect_credential_expiry(self) -> Optional[float]:
    """Check AWS credential expiry. Returns Unix timestamp or None."""
    try:
        # For STS temporary credentials
        sts = self._session.client("sts")
        identity = sts.get_caller_identity()

        # Check if using IAM access keys (have CreateDate but no expiry)
        iam = self._session.client("iam")
        keys = iam.list_access_keys()["AccessKeyMetadata"]
        if keys:
            # IAM access keys don't expire, but we track age
            oldest = min(k["CreateDate"] for k in keys)
            # AWS recommends rotating every 90 days
            age_days = (datetime.utcnow() - oldest.replace(tzinfo=None)).days
            if age_days > 90:
                # Return a synthetic "expiry" at 90 days from creation
                return (oldest + timedelta(days=90)).timestamp()
        return None
    except Exception:
        return None
```

**GitHub connector** (`connectors/github.py`):
```python
def detect_credential_expiry(self) -> Optional[float]:
    """Check GitHub PAT expiry from API response headers."""
    try:
        resp = self._client.get("/")
        expiry_header = resp.headers.get("github-authentication-token-expiration")
        if expiry_header:
            # Format: "2024-01-15 00:00:00 UTC"
            from datetime import datetime
            dt = datetime.strptime(expiry_header, "%Y-%m-%d %H:%M:%S %Z")
            return dt.timestamp()
        return None  # Classic PAT — no expiry
    except Exception:
        return None
```

### Step 3: Extend the validate endpoint response

Update `/api/connectors/{connector_id}/validate` to include expiry info:

```python
@app.get("/api/connectors/{connector_id}/validate")
async def validate_connector(connector_id: str):
    # ... existing validation logic ...

    result = {
        "valid": True,
        "connector_id": connector_id,
        "validated_at": datetime.utcnow().isoformat(),
    }

    # Add expiry detection for supported connectors
    connector = get_connector(connector_id)
    if hasattr(connector, "detect_credential_expiry"):
        expires_at = connector.detect_credential_expiry()
        if expires_at is not None:
            result["expires_at"] = datetime.fromtimestamp(expires_at).isoformat()
            result["days_until_expiry"] = (expires_at - time.time()) / 86400
            result["expiry_warning"] = (expires_at - time.time()) < 7 * 86400

            # Persist metadata
            save_meta(connector_id, CredentialMeta(
                connector_id=connector_id,
                last_validated=time.time(),
                expires_at=expires_at,
                created_at=None,
                source="provider_api",
            ))

    return result
```

### Step 4: Update the desktop UI

In `ConnectorForm.tsx` — show an amber warning badge when credentials are expiring:

```tsx
// After a successful validate call, check for expiry_warning
{validateResult?.expiry_warning && (
  <div className="flex items-center gap-2 px-3 py-2 bg-amber-500/10 border border-amber-500/30 rounded-lg">
    <span className="text-amber-400">⚠</span>
    <span className="text-amber-300 text-sm">
      Credentials expire in {Math.ceil(validateResult.days_until_expiry)} days.
      Rotate them to avoid service disruption.
    </span>
  </div>
)}
```

Also show in the Integrations page connector card for at-a-glance visibility.

---

## Checklist

### Preparation
- [ ] Verify AWS STS/IAM API calls for credential age detection
- [ ] Verify GitHub API response headers for PAT expiry (`github-authentication-token-expiration`)
- [ ] Check if GitLab PAT self-introspection is available (stretch goal)

### Implementation
- [ ] Create `prash/credential_metadata.py` with `CredentialMeta` dataclass and file persistence
- [ ] Add `detect_credential_expiry()` to `connectors/aws.py`
- [ ] Add `detect_credential_expiry()` to `connectors/github.py`
- [ ] Extend `/api/connectors/{id}/validate` response to include `expires_at`, `days_until_expiry`, `expiry_warning`
- [ ] Persist credential metadata to `.prash/credential_meta.json`
- [ ] Update `ConnectorForm.tsx` to show amber warning when `expiry_warning` is true
- [ ] Update `Integrations.tsx` connector card to show expiry status

### Testing
- [ ] Unit test: `CredentialMeta.is_expiring_soon` returns `True` when < 7 days
- [ ] Unit test: `CredentialMeta.is_expired` returns `True` when past expiry
- [ ] Unit test: AWS expiry detection with mocked STS/IAM responses
- [ ] Unit test: GitHub expiry detection with mocked response headers
- [ ] Integration test: validate endpoint returns `expires_at` field
- [ ] All existing tests pass

---

## Anti-Patterns to Avoid

> **🚫 DO NOT store the actual credential expiry date in `.env`.** The `.env` file is for credentials, not metadata. Use a separate `.prash/credential_meta.json` file.

> **🚫 DO NOT make expiry detection blocking.** If the expiry check fails (network error, insufficient IAM permissions), the validate endpoint should still return the validation result — just without expiry info. Never crash the validate call because expiry detection failed.

> **🚫 DO NOT enforce credential rotation.** This task is about DETECTION and WARNING only. Don't prevent the user from using expired credentials — some connectors work with expired tokens in limited ways. Just warn them.

> **🚫 DO NOT hardcode the 7-day warning threshold.** Use an env var or constant: `CREDENTIAL_EXPIRY_WARNING_DAYS = int(os.getenv("LEAR_EXPIRY_WARNING_DAYS", "7"))`.

> **🚫 DO NOT call expiry detection on every API request.** Only check during explicit `validate` calls. The result is cached in `credential_meta.json`.

---

## Exit Criteria

- [ ] **At least AWS + GitHub connectors report credential age/expiry** via `detect_credential_expiry()`
- [ ] **`/api/connectors/{id}/validate` returns `expires_at`** when detectable
- [ ] **UI shows amber warning when less than 7 days from expiry**
- [ ] **Expiry detection does not break existing validate flow** — if detection fails, validate still returns the base result
- [ ] **All existing tests pass**
