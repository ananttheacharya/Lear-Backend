#!/usr/bin/env bash
# Validate S-06 secure headers against a running Lear/FastAPI server.
# Usage: scripts/check_security_headers.sh http://localhost:8000

set -euo pipefail

BASE_URL="${1:-http://localhost:8000}"
TARGET="${BASE_URL%/}/api/system/version"
FAIL=0

echo "Checking security headers on ${TARGET}"
# Prefer HEAD (`curl -I`) for CI friendliness. FastAPI does not automatically
# expose HEAD for every GET route, so fall back to a zero-body GET if a route
# returns 405 while still validating the exact same response headers.
HEADERS="$(curl -sSI "${TARGET}" || true)"
if printf '%s\n' "$HEADERS" | grep -q "^HTTP/.* 405"; then
  HEADERS="$(curl -fsS -D - -o /dev/null "${TARGET}")"
fi

check_header() {
  local header="$1"
  if printf '%s\n' "$HEADERS" | grep -qi "^${header}:"; then
    echo "  OK ${header}"
  else
    echo "  MISSING ${header}" >&2
    FAIL=1
  fi
}

check_header "X-Content-Type-Options"
check_header "X-Frame-Options"
check_header "Strict-Transport-Security"
check_header "Content-Security-Policy"
check_header "Referrer-Policy"
check_header "Permissions-Policy"

if [ "$FAIL" -ne 0 ]; then
  echo "FAILED: one or more security headers are missing." >&2
  exit 1
fi

echo "All required security headers are present."
