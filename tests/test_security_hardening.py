"""Security hardening tests for S-05/S-06."""

from __future__ import annotations

from fastapi.testclient import TestClient

from prash.middleware.security_headers import required_security_header_names
from prash.server import app
from scripts.security import secrets_audit


REQUIRED_HEADERS = tuple(name.lower() for name in required_security_header_names())


def _assert_required_security_headers(response) -> None:
    for header in REQUIRED_HEADERS:
        assert header in response.headers, f"missing {header} on {response.request.url}"


def test_security_headers_on_json_response() -> None:
    with TestClient(app) as client:
        response = client.get("/api/system/version")
    assert response.status_code == 200
    _assert_required_security_headers(response)
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["strict-transport-security"] == "max-age=31536000; includeSubDomains"
    assert "default-src 'self'" in response.headers["content-security-policy"]
    assert "connect-src 'self' http: https: ws: wss:" in response.headers["content-security-policy"]


def test_security_headers_on_html_response() -> None:
    with TestClient(app) as client:
        response = client.get("/demo")
    assert response.status_code == 200
    _assert_required_security_headers(response)
    assert "text/html" in response.headers["content-type"]


def test_security_headers_on_handled_error_response() -> None:
    with TestClient(app) as client:
        response = client.get("/api/connectors/not-a-provider")
    assert response.status_code == 404
    _assert_required_security_headers(response)
    assert response.json()["code"] == "CONNECTOR_NOT_FOUND"


def test_secret_scanner_flags_realistic_provider_secret_assignment() -> None:
    text = "DEEPSEEK_API_KEY=sk-livevalue1234567890abcdefghijklmnopqrstuvwxyz\n"  # pragma: allowlist secret
    findings = secrets_audit.scan_text("scratch.env", text, source="unit")
    assert len(findings) >= 1
    assert {finding.rule_id for finding in findings} <= {"provider-secret-assignment", "openai-compatible-api-key"}
    for finding in findings:
        assert "livevalue1234567890abcdefghijklmnopqrstuvwxyz" not in finding.excerpt
        assert "[REDACTED]" in finding.excerpt


def test_secret_scanner_allows_obvious_test_placeholders() -> None:
    text = (
        "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE\n"
        "GITHUB_TOKEN=github-token-for-test\n"
        "DEEPSEEK_API_KEY=placeholder-value-for-local-development\n"
    )
    findings = secrets_audit.scan_text("tests/fixtures/example.env", text, source="unit")
    assert findings == []
