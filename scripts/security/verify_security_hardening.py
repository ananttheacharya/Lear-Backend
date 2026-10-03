#!/usr/bin/env python3
"""One-command local verification for S-05 and S-06.

Runs the portable secret scans and, when a live server URL is supplied, validates
secure HTTP headers too. This is intentionally lightweight and safe for reviewers
to run before opening or merging a PR.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.security import check_security_headers, secrets_audit  # noqa: E402


def _run_secret_scan(name: str, argv: list[str]) -> bool:
    print(f"[security] {name}")
    code = secrets_audit.main(argv)
    if code != 0:
        print(f"[security] {name} failed", file=sys.stderr)
        return False
    return True


def _run_header_check(base_url: str) -> bool:
    print(f"[security] validating HTTP headers at {base_url}")
    code = check_security_headers.main([base_url])
    if code != 0:
        print("[security] HTTP header validation failed", file=sys.stderr)
        return False
    return True


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Lear security hardening checks.")
    parser.add_argument("--base-url", help="optional live server base URL for S-06 header validation")
    parser.add_argument("--skip-history", action="store_true", help="skip full-history secret scan for a faster local smoke test")
    args = parser.parse_args(argv)

    ok = True
    ok = _run_secret_scan("working-tree secret scan", ["--working-tree"]) and ok
    if not args.skip_history:
        ok = _run_secret_scan("full-history secret scan", ["--history"]) and ok
    if args.base_url:
        ok = _run_header_check(args.base_url) and ok

    if ok:
        print("[security] all requested hardening checks passed")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
