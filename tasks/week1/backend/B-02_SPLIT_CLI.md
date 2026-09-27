# B-02 — Split `cli.py` into Command Modules

**Owner:** Anant
**Priority:** P1
**Status:** ⬜ Not Started
**Estimated effort:** 1–2 days
**Depends on:** Nothing (can be done in parallel with B-01)
**Blocks:** Nothing

---

## Objective

Decompose the 1,361-line `prash/cli.py` (65 KB) into focused command modules. After this task, `cli.py` is the entry-point parser builder only (under 200 lines), and each command's logic lives in `prash/cli/commands/*.py`.

---

## Why This Matters

- **Currently:** `cli.py` contains the argument parser, ALL command implementations (`fix`, `watch`, `investigate`, `run`, `logs`, `audit`, `config`, `notify`), the REPL, environment setup, and output formatting — all in one 65 KB file.
- **After:** Each command is a self-contained module. Adding a new command means adding a new file, not editing a 1,400-line monolith.

---

## Current CLI Commands

From the module docstring and argparse setup:

| Command | Function | Approximate Lines | Description |
|---|---|---|---|
| `prash run <action> <resource>` | `cmd_run()` | ~100 | Execute an action through the pipeline |
| `prash fix <resource>` | `cmd_fix()` | ~300 | Diagnose + recommend fix |
| `prash investigate <resource>` | `cmd_investigate()` | ~80 | Read-only state/logs |
| `prash logs <resource>` | `cmd_logs()` | ~60 | Read/tail pod logs |
| `prash actions` | `cmd_actions()` | ~40 | List registered actions |
| `prash audit` | `cmd_audit()` | ~30 | Show audit log |
| `prash config` | `cmd_config()` | ~30 | Show local config |
| `prash watch` | `cmd_watch()` | ~150 | Poll namespace, notify |
| `prash notify <message>` | `cmd_notify()` | ~40 | Send team notification |
| _(shared)_ | `_export_cluster_env()`, parser builder | ~200 | Environment setup, argparse |

---

## Target Structure

```
prash/
  cli/
    __init__.py          # Package init — exports build_parser() and main()
    parser.py            # Argparse parser construction
    _env.py              # _export_cluster_env() and credential setup
    commands/
      __init__.py
      fix.py             # prash fix
      run.py             # prash run
      investigate.py     # prash investigate
      logs.py            # prash logs
      watch.py           # prash watch
      actions.py         # prash actions
      audit.py           # prash audit
      config.py          # prash config
      notify.py          # prash notify
  cli.py                 # Kept as thin entry-point for backward compat
```

---

## Implementation Plan

### Step 1: Create the `cli/` package structure

```bash
mkdir -p prash/cli/commands
touch prash/cli/__init__.py
touch prash/cli/parser.py
touch prash/cli/_env.py
touch prash/cli/commands/__init__.py
```

### Step 2: Extract shared utilities first

Move `_export_cluster_env()` and any shared helpers to `prash/cli/_env.py`:

```python
# prash/cli/_env.py
"""Shared environment and credential setup for CLI commands."""
from __future__ import annotations
import os
from pathlib import Path


def export_cluster_env() -> None:
    """Load .env credentials into the process environment.
    
    Matches the contract: shell-exported value wins over .env.
    See PRASH_V2.md §10 for the history of this function.
    """
    # ... existing _export_cluster_env() implementation ...
```

### Step 3: Extract each command module

Each command module follows this pattern:

```python
# prash/cli/commands/fix.py
"""prash fix — diagnose a failure and recommend a fix."""
from __future__ import annotations

import argparse
from rich.panel import Panel

from prash.cli._env import export_cluster_env
from prash import ui


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'fix' subcommand with the argument parser."""
    parser = subparsers.add_parser("fix", help="Diagnose a failure and recommend a fix")
    parser.add_argument("resource", help="namespace/pod or owner/repo")
    parser.add_argument("--ci", action="store_true")
    parser.add_argument("--run-id", type=int)
    parser.set_defaults(func=execute)


def execute(args: argparse.Namespace) -> None:
    """Execute the fix command."""
    export_cluster_env()
    # ... existing cmd_fix() implementation ...
```

### Step 4: Build the parser in `parser.py`

```python
# prash/cli/parser.py
"""CLI argument parser construction."""
from __future__ import annotations

import argparse
from prash.cli.commands import fix, run, investigate, logs, watch, actions, audit, config, notify


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="prash", description="Lear — DevOps Agent")
    subparsers = parser.add_subparsers(dest="command")

    # Register each command
    fix.register(subparsers)
    run.register(subparsers)
    investigate.register(subparsers)
    logs.register(subparsers)
    watch.register(subparsers)
    actions.register(subparsers)
    audit.register(subparsers)
    config.register(subparsers)
    notify.register(subparsers)

    return parser
```

### Step 5: Keep `cli.py` as a thin entry point

```python
# prash/cli.py — backward-compatible entry point
"""Thin entry point — delegates to prash.cli package."""
from prash.cli import main

if __name__ == "__main__":
    main()
```

### Step 6: Verify

```bash
# Help output must be identical
prash --help
prash fix --help
prash watch --help

# All CLI tests must pass
pytest tests/test_cli.py -x -q
pytest tests/test_repl.py -x -q
pytest tests/test_fix.py -x -q
```

---

## Checklist

### Preparation
- [ ] Read all 1,361 lines of `cli.py` and map functions to target modules
- [ ] Identify all shared helpers and their callers
- [ ] Note which functions import from other `prash.*` modules (brain, connectors, etc.)

### Extraction (one at a time, test between each)
- [ ] Extract `cli/_env.py` (shared environment setup) → test → commit
- [ ] Extract `cli/commands/actions.py` (simplest) → test → commit
- [ ] Extract `cli/commands/audit.py` → test → commit
- [ ] Extract `cli/commands/config.py` → test → commit
- [ ] Extract `cli/commands/notify.py` → test → commit
- [ ] Extract `cli/commands/logs.py` → test → commit
- [ ] Extract `cli/commands/investigate.py` → test → commit
- [ ] Extract `cli/commands/run.py` → test → commit
- [ ] Extract `cli/commands/watch.py` → test → commit
- [ ] Extract `cli/commands/fix.py` (most complex) → test → commit
- [ ] Create `cli/parser.py` with parser builder
- [ ] Reduce `cli.py` to thin entry point

### Final Verification
- [ ] `cli.py` under 200 lines
- [ ] `prash --help` output unchanged (diff the output before and after)
- [ ] All CLI tests pass: `pytest tests/test_cli.py tests/test_repl.py tests/test_fix.py -x`
- [ ] REPL still works: `prash` (interactive mode)
- [ ] `wc -l prash/cli.py` < 200

---

## Anti-Patterns to Avoid

> **🚫 DO NOT change CLI behavior.** This is a structural refactor. `prash fix`, `prash watch`, etc. must produce identical output. No flag renaming, no behavior changes.

> **🚫 DO NOT break the REPL.** `prash/repl.py` imports from `cli.py`. Make sure the import paths are updated.

> **🚫 DO NOT move server-invocation code into CLI commands.** The CLI has a `serve` function that starts the FastAPI server — this stays in the entry point, not in a command module.

> **🚫 DO NOT create circular imports.** `cli/commands/fix.py` needs `brain/diagnosis_agent.py`, and the brain may need CLI utilities. Use lazy imports if necessary.

> **🚫 DO NOT forget to update the package's `__init__.py` entry points** and any `setup.py`/`pyproject.toml` console_scripts.

---

## Exit Criteria

- [ ] **`cli.py` under 200 lines** — entry point only
- [ ] **All CLI tests pass** — `pytest tests/test_cli.py tests/test_repl.py tests/test_fix.py`
- [ ] **`prash --help` output unchanged** — diff before/after
- [ ] **Each command lives in its own module** in `prash/cli/commands/`
