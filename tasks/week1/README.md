# WEEK 1 — Foundation and Security (Sep 29 – Oct 3)

**Theme:** *"Make it safe and make it clean."*
**Goal:** Security protocols in place, server.py decomposed, UI redesign started, test coverage baseline established.

---

## Task Index

### Security Hardening

| ID | Task | Owner | Priority | Status |
|---|---|---|---|---|
| S-01 | Input validation and sanitization on all API endpoints | Aryan | P0 | ⬜ Not Started |
| S-02 | Rate limiting middleware | Parv | P0 | ⬜ Not Started |
| S-03 | CORS lockdown | Parv | P0 | ⬜ Not Started |
| S-04 | Credential rotation and expiry detection | Aryan | P1 | ⬜ Not Started |
| S-05 | Secrets audit: scan codebase for leaked patterns | Parv | P0 | ⬜ Not Started |
| S-06 | Secure HTTP headers middleware | Parv | P1 | ⬜ Not Started |
| S-07 | WebSocket authentication | Aryan | P1 | ⬜ Not Started |

### Backend Decomposition

| ID | Task | Owner | Priority | Status |
|---|---|---|---|---|
| B-01 | Split `server.py` into route modules | Aryan | P0 | ⬜ Not Started |
| B-02 | Split `cli.py` into command modules | Aryan | P1 | ⬜ Not Started |
| B-03 | Extract shared state from `server.py` | Aryan | P0 | ⬜ Not Started |
| B-04 | API versioning | Parv | P2 | ⬜ Not Started |

### UI Overhaul — Phase 1

| ID | Task | Owner | Priority | Status |
|---|---|---|---|---|
| U-01 | Design system audit and token overhaul | Avi | P0 | ⬜ Not Started |
| U-02 | Sidebar and navigation redesign | Avi | P0 | ⬜ Not Started |
| U-03 | Dashboard redesign | Avi | P0 | ⬜ Not Started |
| U-04 | Component library foundation | Avi | P1 | ⬜ Not Started |

### Testing and Quality Baseline

| ID | Task | Owner | Priority | Status |
|---|---|---|---|---|
| T-01 | Measure current test coverage | Anant | P0 | ⬜ Not Started |
| T-02 | Add missing integration tests for `server.py` endpoint contracts | Anant | P1 | ⬜ Not Started |
| T-03 | Frontend test infrastructure | Anant | P1 | ⬜ Not Started |

---

## Dependency Graph

```
S-05 (secrets audit)          ─── no deps, run first
S-01 (input validation)       ─── no deps, parallel with B-01
S-03 (CORS lockdown)          ─── no deps
S-02 (rate limiting)          ─── best after B-01 (route modules exist)
S-06 (HTTP headers)           ─── no deps
S-07 (WebSocket auth)         ─── no deps

B-03 (extract shared state)   ─── should start BEFORE B-01
B-01 (split server.py)        ─── depends on B-03 (state is extracted first)
B-02 (split cli.py)           ─── no deps, parallel with B-01
B-04 (API versioning)         ─── depends on B-01 (routes exist as modules)

S-04 (credential expiry)      ─── depends on S-01 (validated endpoints)

U-01 (design tokens)          ─── no deps, start day 1
U-02 (sidebar redesign)       ─── depends on U-01 (tokens exist)
U-03 (dashboard redesign)     ─── depends on U-01 (tokens exist)
U-04 (component library)      ─── depends on U-01 (tokens exist)

T-01 (coverage baseline)      ─── no deps, run day 1
T-02 (integration tests)      ─── no deps, but easier after B-01
T-03 (frontend tests)         ─── no deps
```

---

## Friday Demo (Oct 3) — Exit Criteria

- [ ] Decomposed server running — all tests green
- [ ] Security middleware active (rate limiting, CORS, HTTP headers)
- [ ] First design system tokens applied to Sidebar + Dashboard
- [ ] Test coverage baseline documented
