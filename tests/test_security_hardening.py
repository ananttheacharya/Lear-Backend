"""Security hardening tests for S-05/S-06."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.testclient import TestClient

from prash.middleware.security_headers import SecurityHeadersMiddleware, required_security_header_names
from prash.server import app
from scripts.security import check_security_headers, secrets_audit


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


def test_security_headers_on_streaming_response() -> None:
    probe = FastAPI()
    probe.add_middleware(SecurityHeadersMiddleware)

    @probe.get("/stream")
    def stream():
        return StreamingResponse(iter(["one\n", "two\n"]), media_type="text/plain")

    with TestClient(probe) as client:
        response = client.get("/stream")
    assert response.status_code == 200
    assert response.text == "one\ntwo\n"
    _assert_required_security_headers(response)


def test_security_headers_respect_explicit_route_header() -> None:
    probe = FastAPI()
    probe.add_middleware(SecurityHeadersMiddleware)

    @probe.get("/custom")
    def custom():
        return StreamingResponse(
            iter(["ok"]),
            media_type="text/plain",
            headers={"Content-Security-Policy": "default-src 'none'"},
        )

    with TestClient(probe) as client:
        response = client.get("/custom")
    _assert_required_security_headers(response)
    assert response.headers["content-security-policy"] == "default-src 'none'"


def test_security_headers_support_csp_environment_override(monkeypatch) -> None:
    monkeypatch.setenv("LEAR_CSP", "default-src 'none'; connect-src 'self'")
    with TestClient(app) as client:
        response = client.get("/api/system/version")
    assert response.status_code == 200
    assert response.headers["content-security-policy"] == "default-src 'none'; connect-src 'self'"


def test_python_security_header_checker_accepts_valid_headers() -> None:
    headers = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'; connect-src 'self' ws: wss:",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    }
    assert check_security_headers.validate_headers(headers) == []


def test_python_security_header_checker_reports_missing_and_bad_values() -> None:
    failures = check_security_headers.validate_headers({"X-Frame-Options": "SAMEORIGIN"})
    assert "X-Frame-Options expected 'DENY', got 'SAMEORIGIN'" in failures
    assert "missing X-Content-Type-Options" in failures
    assert any("Content-Security-Policy" in item for item in failures)


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
