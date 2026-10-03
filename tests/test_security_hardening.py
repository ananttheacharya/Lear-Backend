"""Security hardening tests for S-05/S-06."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.testclient import TestClient

from prash.middleware.security_headers import (
    HSTS_VALUE,
    SecurityHeadersMiddleware,
    required_security_header_names,
    security_headers,
)
from prash.server import app
from scripts.security import check_security_headers, secrets_audit


LOCAL_REQUIRED_HEADERS = tuple(name.lower() for name in required_security_header_names())
TRANSPORT_REQUIRED_HEADERS = tuple(
    name.lower() for name in required_security_header_names(include_transport_security=True)
)


def _assert_required_security_headers(response, *, include_transport_security: bool = False) -> None:
    required = TRANSPORT_REQUIRED_HEADERS if include_transport_security else LOCAL_REQUIRED_HEADERS
    for header in required:
        assert header in response.headers, f"missing {header} on {response.request.url}"


def _make_probe_app() -> FastAPI:
    probe = FastAPI()
    probe.add_middleware(SecurityHeadersMiddleware)
    return probe


def test_security_headers_on_json_response_local_http_no_transport_upgrade() -> None:
    with TestClient(app) as client:
        response = client.get("/api/system/version")
    assert response.status_code == 200
    _assert_required_security_headers(response)
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert "strict-transport-security" not in response.headers
    csp = response.headers["content-security-policy"]
    assert "default-src 'self'" in csp
    assert "connect-src 'self' http: https: ws: wss:" in csp
    assert "upgrade-insecure-requests" not in csp


def test_security_headers_on_html_response() -> None:
    with TestClient(app) as client:
        response = client.get("/demo")
    assert response.status_code == 200
    _assert_required_security_headers(response)
    assert "strict-transport-security" not in response.headers
    assert "text/html" in response.headers["content-type"]


def test_security_headers_on_handled_error_response() -> None:
    with TestClient(app) as client:
        response = client.get("/api/connectors/not-a-provider")
    assert response.status_code == 404
    _assert_required_security_headers(response)
    assert response.json()["code"] == "CONNECTOR_NOT_FOUND"


def test_security_headers_on_streaming_response() -> None:
    probe = _make_probe_app()

    @probe.get("/stream")
    def stream():
        return StreamingResponse(iter(["one\n", "two\n"]), media_type="text/plain")

    with TestClient(probe) as client:
        response = client.get("/stream")
    assert response.status_code == 200
    assert response.text == "one\ntwo\n"
    _assert_required_security_headers(response)
    assert "strict-transport-security" not in response.headers


def test_security_headers_enable_transport_security_on_https_request() -> None:
    probe = _make_probe_app()

    @probe.get("/secure")
    def secure():
        return {"ok": True}

    with TestClient(probe, base_url="https://testserver") as client:
        response = client.get("/secure")
    _assert_required_security_headers(response, include_transport_security=True)
    assert response.headers["strict-transport-security"] == HSTS_VALUE
    assert "upgrade-insecure-requests" in response.headers["content-security-policy"]


def test_security_headers_enable_transport_security_from_forwarded_proto() -> None:
    probe = _make_probe_app()

    @probe.get("/proxied")
    def proxied():
        return {"ok": True}

    with TestClient(probe) as client:
        response = client.get("/proxied", headers={"X-Forwarded-Proto": "https"})
    assert response.headers["strict-transport-security"] == HSTS_VALUE
    assert "upgrade-insecure-requests" in response.headers["content-security-policy"]


def test_security_headers_enable_transport_security_in_production(monkeypatch) -> None:
    monkeypatch.setenv("ENVIRONMENT", "production")
    headers = security_headers(is_https=False)
    assert headers["Strict-Transport-Security"] == HSTS_VALUE
    assert "upgrade-insecure-requests" in headers["Content-Security-Policy"]


def test_security_headers_respect_explicit_route_header() -> None:
    probe = _make_probe_app()

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
    assert "strict-transport-security" not in response.headers


def test_security_headers_support_csp_environment_override(monkeypatch) -> None:
    monkeypatch.setenv("LEAR_CSP", "default-src 'none'; connect-src 'self'")
    with TestClient(app) as client:
        response = client.get("/api/system/version")
    assert response.status_code == 200
    assert response.headers["content-security-policy"] == "default-src 'none'; connect-src 'self'"
    assert "strict-transport-security" not in response.headers


def test_python_security_header_checker_accepts_valid_local_headers() -> None:
    headers = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Content-Security-Policy": "default-src 'self'; connect-src 'self' ws: wss:",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    }
    assert check_security_headers.validate_headers(headers) == []


def test_python_security_header_checker_accepts_valid_https_headers() -> None:
    headers = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Strict-Transport-Security": HSTS_VALUE,
        "Content-Security-Policy": "default-src 'self'; connect-src 'self' ws: wss:; upgrade-insecure-requests;",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    }
    assert check_security_headers.validate_headers(headers, expect_transport_security=True) == []


def test_python_security_header_checker_requires_upgrade_for_https_headers() -> None:
    headers = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Strict-Transport-Security": HSTS_VALUE,
        "Content-Security-Policy": "default-src 'self'; connect-src 'self' ws: wss:",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    }
    failures = check_security_headers.validate_headers(headers, expect_transport_security=True)
    assert "Content-Security-Policy missing upgrade-insecure-requests for HTTPS/production" in failures


def test_python_security_header_checker_reports_missing_bad_and_local_hsts_values() -> None:
    failures = check_security_headers.validate_headers({"X-Frame-Options": "SAMEORIGIN"})
    assert "X-Frame-Options expected 'DENY', got 'SAMEORIGIN'" in failures
    assert "missing X-Content-Type-Options" in failures
    assert any("Content-Security-Policy" in item for item in failures)

    local_failures = check_security_headers.validate_headers(
        {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Strict-Transport-Security": HSTS_VALUE,
            "Content-Security-Policy": "default-src 'self'; connect-src 'self'; upgrade-insecure-requests;",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
        }
    )
    assert "Strict-Transport-Security must be absent on local/plain HTTP" in local_failures
    assert "Content-Security-Policy must not force upgrade-insecure-requests on local/plain HTTP" in local_failures


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
