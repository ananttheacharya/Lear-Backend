#!/usr/bin/env python3
"""Cross-platform S-06 security header checker.

This mirrors ``scripts/check_security_headers.sh`` but runs anywhere Python runs,
including Windows CI shells that do not have Bash/curl available.
"""
from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request
from collections.abc import Mapping
from typing import Sequence

REQUIRED_HEADERS = (
    "X-Content-Type-Options",
    "X-Frame-Options",
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "Referrer-Policy",
    "Permissions-Policy",
)

EXPECTED_VALUES = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}


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


def validate_headers(headers: Mapping[str, str], *, strict_values: bool = True) -> list[str]:
    normalized = {key.lower(): value for key, value in headers.items()}
    failures: list[str] = []
    for name in REQUIRED_HEADERS:
        value = normalized.get(name.lower())
        if value is None:
            failures.append(f"missing {name}")
            continue
        if strict_values and name in EXPECTED_VALUES and value != EXPECTED_VALUES[name]:
            failures.append(f"{name} expected {EXPECTED_VALUES[name]!r}, got {value!r}")
    csp = normalized.get("content-security-policy", "")
    if "connect-src" not in csp:
        failures.append("Content-Security-Policy missing connect-src for API/SSE/WebSocket clients")
    return failures


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Lear S-06 security headers on a live server.")
    parser.add_argument("base_url", nargs="?", default="http://localhost:8000")
    parser.add_argument("--path", default="/api/system/version")
    parser.add_argument("--no-strict-values", action="store_true", help="only require header presence")
    args = parser.parse_args(argv)

    try:
        headers = fetch_headers(args.base_url, args.path)
        failures = validate_headers(headers, strict_values=not args.no_strict_values)
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
