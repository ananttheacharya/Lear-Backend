#!/usr/bin/env bash
# Run Lear's complete local secret audit.
#
# This prefers the upstream gitleaks binary when installed, then always runs the
# bundled redacted scanner so the command is useful on fresh contributor
# machines too.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

if command -v gitleaks >/dev/null 2>&1; then
  echo "[security] running gitleaks full-history scan"
  gitleaks detect --source . --config .gitleaks.toml --redact --verbose
else
  echo "[security] gitleaks not found; skipping upstream gitleaks scan"
  echo "[security] install from https://github.com/gitleaks/gitleaks for the full rule set"
fi

echo "[security] running Lear fallback working-tree scan"
python scripts/security/secrets_audit.py --working-tree

echo "[security] running Lear fallback full-history scan"
python scripts/security/secrets_audit.py --history

echo "[security] secret audit completed cleanly"
