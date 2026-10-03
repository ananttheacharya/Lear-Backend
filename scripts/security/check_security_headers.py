#!/usr/bin/env python3
"""Cross-platform S-06 security header checker.

Runs anywhere Python runs, including Windows, macOS, Linux, and CI shells. HSTS
is expected only for HTTPS/production contexts because Lear's desktop/dev server
uses plain local HTTP.
"""
from __future__ import annotations

import argparse
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Mapping
from typing import Sequence

BASE_REQUIRED_HEADERS = (
    "X-Content-Type-Options",
    "X-Frame-Options",
    "Content-Security-Policy",
    "Referrer-Policy",
    "Permissions-Policy",
)

TRANSPORT_REQUIRED_HEADERS = ("Strict-Transport-Security",)

EXPECTED_BASE_VALUES = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}

EXPECTED_TRANSPORT_VALUES = {
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
}


def _is_production() -> bool:
    return any(
        os.getenv(key, "").strip().lower() == "production"
        for key in ("ENVIRONMENT", "LEAR_ENVIRONMENT", "PRASH_ENVIRONMENT")
    )


def should_expect_transport_security(base_url: str, *, production: bool | None = None) -> bool:
    """Return whether HSTS / upgrade-insecure-requests should be present."""
    is_https = urllib.parse.urlparse(base_url).scheme.lower() == "https"
    return is_https or (_is_production() if production is None else production)


def _request_headers(url: str, method: str) -> tuple[int, Mapping[str, str]]:
    req = urllib.request.Request(url, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, dict(resp.headers.items())
    except urllib.error.HTTPError as exc:
        # 405 on HEAD is acceptable; caller decides whether to retry GET.
        return exc.code, dict(exc.headers.items())


def fetch_headers(base_url: str, path: str = "/api/system/version") -> Mapping[str, str]:
    target = base_url.rstrip("/") + path
    status, headers = _request_headers(target, "HEAD")
    if status == 405:
        status, headers = _request_headers(target, "GET")
    if status >= 400:
        raise RuntimeError(f"{target} returned HTTP {status}")
    return headers


def validate_headers(
    headers: Mapping[str, str],
    *,
    strict_values: bool = True,
    expect_transport_security: bool = False,
) -> list[str]:
    """Validate S-06 headers.

    ``expect_transport_security`` should be true for HTTPS / production checks
    and false for local HTTP checks.
    """
    normalized = {key.lower(): value for key, value in headers.items()}
    required = BASE_REQUIRED_HEADERS + (TRANSPORT_REQUIRED_HEADERS if expect_transport_security else ())
    expected_values = dict(EXPECTED_BASE_VALUES)
    if expect_transport_security:
        expected_values.update(EXPECTED_TRANSPORT_VALUES)

    failures: list[str] = []
    for name in required:
        value = normalized.get(name.lower())
        if value is None:
            failures.append(f"missing {name}")
            continue
        if strict_values and name in expected_values and value != expected_values[name]:
            failures.append(f"{name} expected {expected_values[name]!r}, got {value!r}")

    if not expect_transport_security and "strict-transport-security" in normalized:
        failures.append("Strict-Transport-Security must be absent on local/plain HTTP")

    csp = normalized.get("content-security-policy", "")
    if "connect-src" not in csp:
        failures.append("Content-Security-Policy missing connect-src for API/SSE/WebSocket clients")
    has_upgrade = "upgrade-insecure-requests" in csp
    if expect_transport_security and not has_upgrade:
        failures.append("Content-Security-Policy missing upgrade-insecure-requests for HTTPS/production")
    elif not expect_transport_security and has_upgrade:
        failures.append("Content-Security-Policy must not force upgrade-insecure-requests on local/plain HTTP")
    return failures


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Lear S-06 security headers on a live server.")
    parser.add_argument("base_url", nargs="?", default="http://localhost:8000")
    parser.add_argument("--path", default="/api/system/version")
    parser.add_argument("--expect-transport-security", action="store_true", help="require HSTS and upgrade-insecure-requests")
    parser.add_argument("--no-strict-values", action="store_true", help="only require header presence")
    args = parser.parse_args(argv)

    expect_transport_security = args.expect_transport_security or should_expect_transport_security(args.base_url)
    try:
        headers = fetch_headers(args.base_url, args.path)
        failures = validate_headers(
            headers,
            strict_values=not args.no_strict_values,
            expect_transport_security=expect_transport_security,
        )
    except Exception as exc:  # pragma: no cover - CLI guardrail
        print(f"security header check failed: {exc}", file=sys.stderr)
        return 1

    if failures:
        print("Security header validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("All required security headers are present and valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
