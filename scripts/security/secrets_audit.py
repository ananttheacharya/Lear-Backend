#!/usr/bin/env python3
"""Secret-pattern scanner used as Lear's portable safety net.

The S-05 control standardizes on gitleaks. This script intentionally does not
replace gitleaks; it complements it in two places where a tiny, repo-local tool
is valuable:

* the committed pre-commit hook can still block obvious leaks on machines where
  the gitleaks binary is not installed yet; and
* CI/local audits can emit a redacted JSON summary without storing raw secrets.

When gitleaks is installed the hook runs it first, then this scanner as a
second pass for Lear-specific credential names.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]

SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("aws-access-key-id", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("aws-secret-access-key", re.compile(r"(?i)\bAWS_SECRET_ACCESS_KEY\b\s*[:=]\s*['\"]?([A-Za-z0-9/+=]{35,})")),
    ("github-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    ("gitlab-token", re.compile(r"\bglpat-[A-Za-z0-9_-]{20,}\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("openai-compatible-api-key", re.compile(r"\bsk-[A-Za-z0-9_-]{32,}\b")),
    ("private-key", re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA |)?PRIVATE KEY-----")),
    (
        "provider-secret-assignment",
        re.compile(
            r"(?i)\b(?:DEEPSEEK|KIMI|OPENAI|ANTHROPIC|GEMINI|GOOGLE|DATADOG|DD|PAGERDUTY|SNYK|VERCEL|TWILIO|SLACK|DISCORD)_[A-Z0-9_]*(?:KEY|TOKEN|SECRET|WEBHOOK|PASSWORD)\b"
            r"\s*[:=]\s*['\"]?([A-Za-z0-9_./+=:-]{24,})"
        ),
    ),
)

GIT_GREP_PATTERN = (
    r"(AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9_]{20,}|"
    r"glpat-[A-Za-z0-9_-]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|"
    r"AIza[0-9A-Za-z_-]{35}|sk-[A-Za-z0-9_-]{32,}|"
    r"-----BEGIN (RSA |OPENSSH |EC |DSA |)?PRIVATE KEY-----|"
    r"(AWS_SECRET_ACCESS_KEY|DEEPSEEK_[A-Z0-9_]*(KEY|TOKEN|SECRET|PASSWORD)|"
    r"KIMI_[A-Z0-9_]*(KEY|TOKEN|SECRET|PASSWORD)|OPENAI_[A-Z0-9_]*(KEY|TOKEN|SECRET|PASSWORD)|"
    r"ANTHROPIC_[A-Z0-9_]*(KEY|TOKEN|SECRET|PASSWORD)|GEMINI_[A-Z0-9_]*(KEY|TOKEN|SECRET|PASSWORD)|"
    r"DATADOG_[A-Z0-9_]*(KEY|TOKEN|SECRET|PASSWORD)|DD_[A-Z0-9_]*(KEY|TOKEN|SECRET|PASSWORD)|"
    r"PAGERDUTY_[A-Z0-9_]*(KEY|TOKEN|SECRET|PASSWORD)|SNYK_[A-Z0-9_]*(KEY|TOKEN|SECRET|PASSWORD)|"
    r"VERCEL_[A-Z0-9_]*(KEY|TOKEN|SECRET|PASSWORD)|TWILIO_[A-Z0-9_]*(KEY|TOKEN|SECRET|PASSWORD)|"
    r"SLACK_[A-Z0-9_]*(KEY|TOKEN|SECRET|WEBHOOK|PASSWORD)|DISCORD_[A-Z0-9_]*(KEY|TOKEN|SECRET|WEBHOOK|PASSWORD))"
    r"[[:space:]]*[:=][[:space:]]*['\"]?[A-Za-z0-9_./+=:-]{24,})"
)

SAFE_WORDS = (
    "example",
    "fake",
    "dummy",
    "mock",
    "placeholder",
    "changeme",
    "change_me",
    "redacted",
    "not-a-secret",
    "not_a_secret",
    "testing",
    "test-only",
    "unit-test",
    "sample",
)

EXACT_ALLOWLIST = {
    "AKIAIOSFODNN7EXAMPLE",  # AWS documentation example key, not a credential.
    "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",  # AWS documentation example secret.
    "ghp_secretTokenLongerValue123456",  # historical unit-test fixture, not a provider token.
    "AKIASUPERSECRETVALUE",  # historical redaction unit-test fixture, not an AWS key.
}

SKIP_PATH_PATTERNS = tuple(
    re.compile(pattern)
    for pattern in (
        r"(^|/)\.git(/|$)",
        r"(^|/)node_modules(/|$)",
        r"(^|/)\.venv(/|$)",
        r"(^|/)dist(/|$)",
        r"(^|/)build(/|$)",
        r"(^|/)coverage(/|$)",
        r"(^|/)desktop/package-lock\.json$",
        r"(^|/)uv\.lock$",
        r"(^|/)\.pytest_cache(/|$)",
        r"(^|/)\.ruff_cache(/|$)",
    )
)


@dataclass(frozen=True)
class Finding:
    rule_id: str
    path: str
    line: int
    source: str
    commit: str | None
    excerpt: str


def _run_git(args: Sequence[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        errors="replace",
        check=check,
    )


def _is_skipped_path(path: str) -> bool:
    normalized = path.replace(os.sep, "/")
    return any(pattern.search(normalized) for pattern in SKIP_PATH_PATTERNS)


def _extract_secret(match: re.Match[str]) -> str:
    for group in match.groups():
        if group and len(group) >= 16:
            return group
    return match.group(0)


def _is_allowlisted(secret: str, line: str, path: str) -> bool:
    # Only the matched value / source line may carry a placeholder marker. A
    # path named "tests/..." is not enough to suppress a real-looking secret.
    del path
    lowered = f"{secret}\n{line}".lower()
    if secret in EXACT_ALLOWLIST:
        return True
    if "pragma: allowlist secret" in lowered or "gitleaks:allow" in lowered:
        return True
    return any(word in lowered for word in SAFE_WORDS)


def _redact_line(line: str, secret: str) -> str:
    if not secret:
        return line[:240]
    if len(secret) <= 8:
        marker = "[REDACTED]"
    else:
        marker = f"{secret[:3]}...[REDACTED]...{secret[-3:]}"
    return line.replace(secret, marker)[:240]


def scan_text(path: str, text: str, *, source: str, commit: str | None = None) -> list[Finding]:
    if _is_skipped_path(path):
        return []
    findings: list[Finding] = []
    seen: set[tuple[str, int, str]] = set()
    for line_no, line in enumerate(text.splitlines(), start=1):
        for rule_id, pattern in SECRET_PATTERNS:
            for match in pattern.finditer(line):
                secret = _extract_secret(match)
                if _is_allowlisted(secret, line, path):
                    continue
                key = (rule_id, line_no, secret)
                if key in seen:
                    continue
                seen.add(key)
                findings.append(
                    Finding(
                        rule_id=rule_id,
                        path=path,
                        line=line_no,
                        source=source,
                        commit=commit,
                        excerpt=_redact_line(line, secret),
                    )
                )
    return findings


def staged_files() -> list[str]:
    proc = _run_git(["diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"])
    return [item for item in proc.stdout.split("\0") if item and not _is_skipped_path(item)]


def scan_staged() -> list[Finding]:
    findings: list[Finding] = []
    for path in staged_files():
        proc = _run_git(["show", f":{path}"], check=False)
        if proc.returncode != 0:
            continue
        findings.extend(scan_text(path, proc.stdout, source="staged"))
    return findings


def tracked_and_untracked_files() -> list[str]:
    proc = _run_git(["ls-files", "--cached", "--others", "--exclude-standard", "-z"])
    return [item for item in proc.stdout.split("\0") if item and not _is_skipped_path(item)]


def scan_working_tree() -> list[Finding]:
    findings: list[Finding] = []
    for path in tracked_and_untracked_files():
        full_path = REPO_ROOT / path
        try:
            data = full_path.read_bytes()
        except OSError:
            continue
        if b"\0" in data[:4096]:
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            text = data.decode("utf-8", errors="replace")
        findings.extend(scan_text(path, text, source="working-tree"))
    return findings


def scan_history() -> list[Finding]:
    revs = _run_git(["rev-list", "--all"]).stdout.splitlines()
    if not revs:
        return []
    pathspecs = ["."] + [f":!{pattern}" for pattern in ("uv.lock", "desktop/package-lock.json")]
    proc = _run_git(
        ["grep", "-I", "-n", "-E", GIT_GREP_PATTERN, *revs, "--", *pathspecs],
        check=False,
    )
    if proc.returncode == 1:
        return []
    if proc.returncode not in (0, 1):
        raise RuntimeError(proc.stderr.strip() or f"git grep failed with exit {proc.returncode}")

    findings: list[Finding] = []
    seen: set[tuple[str, str, int, str]] = set()
    for raw in proc.stdout.splitlines():
        try:
            commit, rest = raw.split(":", 1)
            path, line_s, line = rest.split(":", 2)
            line_no = int(line_s)
        except ValueError:
            continue
        if _is_skipped_path(path):
            continue
        for finding in scan_text(path, line, source="history", commit=commit):
            normalized = (finding.rule_id, finding.path, finding.line, finding.excerpt)
            if normalized in seen:
                continue
            seen.add(normalized)
            findings.append(
                Finding(
                    rule_id=finding.rule_id,
                    path=finding.path,
                    line=line_no,
                    source=finding.source,
                    commit=finding.commit,
                    excerpt=finding.excerpt,
                )
            )
    return findings


def write_report(path: Path, findings: Iterable[Finding], modes: Sequence[str]) -> None:
    items = [asdict(f) for f in findings]
    payload = {
        "tool": "scripts/security/secrets_audit.py",
        "modes": list(modes),
        "redacted": True,
        "finding_count": len(items),
        "findings": items,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def print_findings(findings: Sequence[Finding]) -> None:
    if not findings:
        print("No secret-pattern findings detected.")
        return
    print(f"Detected {len(findings)} potential secret-pattern finding(s):", file=sys.stderr)
    for finding in findings[:50]:
        commit = f" commit={finding.commit[:12]}" if finding.commit else ""
        print(
            f"- {finding.rule_id} {finding.path}:{finding.line} [{finding.source}{commit}] {finding.excerpt}",
            file=sys.stderr,
        )
    if len(findings) > 50:
        print(f"... {len(findings) - 50} more redacted findings omitted from console output", file=sys.stderr)


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan Lear sources for leaked secret patterns.")
    parser.add_argument("--staged", action="store_true", help="scan staged changes only")
    parser.add_argument("--history", action="store_true", help="scan every reachable git commit")
    parser.add_argument("--working-tree", action="store_true", help="scan tracked and untracked working-tree files")
    parser.add_argument("--report", type=Path, help="write a redacted JSON report")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    modes: list[str] = []
    findings: list[Finding] = []

    if args.staged:
        modes.append("staged")
        findings.extend(scan_staged())
    if args.history:
        modes.append("history")
        findings.extend(scan_history())
    if args.working_tree or not modes:
        modes.append("working-tree")
        findings.extend(scan_working_tree())

    print_findings(findings)
    if args.report:
        write_report(args.report, findings, modes)
        print(f"Redacted report written to {args.report}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
