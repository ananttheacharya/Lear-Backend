#!/usr/bin/env python3
"""Install Lear's versioned git hooks into this checkout.

Git does not clone hook files into .git/hooks automatically. Running this script
points the repository at the committed .githooks directory so the S-05 secret
scanner blocks future leaks locally without copying untracked hook files around.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    hooks_dir = ROOT / ".githooks"
    hook = hooks_dir / "pre-commit"
    if not hook.exists():
        raise SystemExit(f"missing hook: {hook}")
    hook.chmod(hook.stat().st_mode | 0o111)
    subprocess.run(["git", "config", "core.hooksPath", ".githooks"], cwd=ROOT, check=True)
    print("Installed Lear git hooks: core.hooksPath=.githooks")
    print("Pre-commit now runs gitleaks when available plus the bundled fallback scanner.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
