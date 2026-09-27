# T-01 — Measure Current Test Coverage

**Owner:** Anant
**Priority:** P0
**Status:** ⬜ Not Started
**Estimated effort:** 0.5 day
**Depends on:** Nothing (start day 1)
**Blocks:** T-02 (need to know what's missing before adding tests)

---

## Objective

Run `pytest --cov` for the backend and `vitest --coverage` for the frontend. Establish baseline coverage numbers. Identify the 10 lowest-covered modules. Document the results as a CI artifact and a reference for the team.

---

## Why This Matters

- **Currently:** We have 41 test files and 800+ passing tests, but we don't know what percentage of code they cover. Some modules might be at 95%, others at 5%. Without a baseline, we can't set improvement targets or catch coverage regressions.
- **After:** Everyone knows the exact coverage numbers. The 10 lowest-covered modules are the priority targets for T-02. Coverage reports are generated in CI on every PR.

---

## Implementation Plan

### Step 1: Run backend coverage

```bash
# Install coverage tools if not present
pip install pytest-cov

# Run with coverage — all test files
pytest tests/ --cov=prash --cov-report=html:coverage_html --cov-report=json:coverage.json --cov-report=term-missing -q

# The key outputs:
# - Terminal: summary with missing lines
# - coverage_html/: browsable HTML report
# - coverage.json: machine-readable for CI
```

### Step 2: Run frontend coverage

```bash
cd desktop

# Ensure vitest coverage provider is installed
npm install -D @vitest/coverage-v8

# Run with coverage
npx vitest run --coverage --reporter=json --outputFile=coverage.json
```

If `vitest.config.ts` doesn't have coverage configured, add:

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'json'],
      include: ['src/**/*.{ts,tsx}'],
      exclude: ['src/**/*.test.{ts,tsx}', 'src/**/*.d.ts'],
    },
  },
});
```

### Step 3: Identify the 10 lowest-covered modules

Parse `coverage.json` and sort by coverage percentage:

```python
# scripts/find_lowest_coverage.py
import json

with open("coverage.json") as f:
    data = json.load(f)

# pytest-cov format
files = []
for filename, stats in data.get("files", {}).items():
    if filename.startswith("prash/"):
        pct = stats["summary"]["percent_covered"]
        files.append((filename, pct, stats["summary"]["missing_lines"]))

files.sort(key=lambda x: x[1])

print("=" * 60)
print("10 LOWEST-COVERED MODULES")
print("=" * 60)
for name, pct, missing in files[:10]:
    print(f"  {pct:5.1f}%  ({missing:3d} uncovered lines)  {name}")
```

### Step 4: Document the baseline

Create `docs/coverage-baseline.md`:

```markdown
# Coverage Baseline — [Date]

## Backend (pytest --cov)

| Module | Coverage | Missing Lines |
|---|---|---|
| prash/server.py | XX% | YY |
| prash/cli.py | XX% | YY |
| ... | ... | ... |

**Overall backend coverage:** XX%

## Frontend (vitest --coverage)

| Module | Coverage | Missing Lines |
|---|---|---|
| src/components/Dashboard.tsx | XX% | YY |
| ... | ... | ... |

**Overall frontend coverage:** XX%

## 10 Lowest-Covered Modules (Backend)

1. `prash/FOO.py` — X%
2. ...

## 10 Lowest-Covered Modules (Frontend)

1. `src/components/FOO.tsx` — X%
2. ...
```

### Step 5: Add coverage to CI

Add to the GitHub Actions workflow (or create one):

```yaml
# .github/workflows/coverage.yml
name: Test Coverage

on: [push, pull_request]

jobs:
  backend-coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install -r requirements.txt pytest-cov
      - run: pytest tests/ --cov=prash --cov-report=json --cov-report=term -q
      - uses: actions/upload-artifact@v4
        with:
          name: backend-coverage
          path: coverage.json

  frontend-coverage:
    runs-on: ubuntu-latest
    defaults:
      run: { working-directory: desktop }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci
      - run: npx vitest run --coverage
      - uses: actions/upload-artifact@v4
        with:
          name: frontend-coverage
          path: desktop/coverage/
```

---

## Checklist

### Backend
- [ ] Install `pytest-cov` if not present
- [ ] Run `pytest tests/ --cov=prash --cov-report=html --cov-report=json --cov-report=term-missing`
- [ ] Verify all 800+ tests pass
- [ ] Record overall backend coverage percentage
- [ ] Record per-module coverage for all `prash/` modules
- [ ] Identify 10 lowest-covered backend modules

### Frontend
- [ ] Install `@vitest/coverage-v8` if not present
- [ ] Configure vitest coverage in `vitest.config.ts`
- [ ] Run `npx vitest run --coverage`
- [ ] Record overall frontend coverage percentage
- [ ] Record per-component coverage for all `src/components/` files
- [ ] Identify 10 lowest-covered frontend modules

### Documentation
- [ ] Create `docs/coverage-baseline.md` with all numbers
- [ ] Include the date and commit hash for reproducibility
- [ ] List the 10 lowest-covered modules for both backend and frontend

### CI
- [ ] Coverage report generated as CI artifact on every push/PR
- [ ] Coverage numbers visible in PR comments or CI output
- [ ] HTML coverage report browsable as CI artifact

---

## Anti-Patterns to Avoid

> **🚫 DO NOT set a coverage target yet.** This task is about MEASURING, not about achieving a number. The roadmap says 70% backend / 50% frontend by end of Week 3 — that's the target. This task establishes where we ARE, not where we need to be.

> **🚫 DO NOT exclude modules from coverage to inflate numbers.** Measure everything in `prash/`. If a module is at 0%, that's important information. Don't hide it.

> **🚫 DO NOT run only a subset of tests.** Run ALL tests: `pytest tests/`. Some tests might be slow — that's fine for a baseline measurement. Note any tests that are skipped and why.

> **🚫 DO NOT commit the HTML coverage report to the repo.** It's large and generated. Add `coverage_html/` and `coverage.json` to `.gitignore`. Upload as CI artifacts instead.

> **🚫 DO NOT block on CI setup.** If CI takes too long to configure, run coverage locally first and document the numbers. CI integration can be a follow-up commit.

---

## Exit Criteria

- [ ] **Coverage report artifact in CI** — or at minimum, documented locally with commit hash
- [ ] **Baseline numbers documented** — `docs/coverage-baseline.md` with per-module breakdown
- [ ] **10 lowest-covered modules identified** — for both backend and frontend
- [ ] **All tests pass** — coverage run doesn't break anything
