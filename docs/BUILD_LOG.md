# LecMerge — Build Log

Source of truth: `LecMerge_Overnight_Agent_Build_Spec.md` (Section 12).
Remote: https://github.com/rahulratul/LecMerge

## Phase status

| Phase | Name | Branch | Status |
|---|---|---|---|
| 0 | Workspace inspection, GitHub remote setup, scope lock | `main` (bootstrap) → `develop` | in progress |
| 1 | Minimal runnable project scaffold | `feature/p1-project-scaffold` | not started |
| 2 | Domain logic and three design patterns (TDD) | `feature/p2-domain-patterns` | not started |
| 3 | Database, repository, application service | `feature/p3-db-and-services` | not started |
| 4 | GUI: course, lecture, block, fragment workflow | `feature/p4-gui-workflow` | not started |
| 5 | Analysis, merge workspace, Markdown export | `feature/p5-analysis-and-merge` | not started |
| 6 | REST API and OpenAPI documentation | `feature/p6-rest-api-openapi` | not started |
| 7 | Test hardening, Selenium, GitHub CI, Git evidence | `feature/p7-tests-selenium-ci` | not started |
| 8 | Final documentation, release merge, submission readiness | `develop` → `main` | not started |

---

## Phase 0 — Workspace inspection, GitHub remote setup, scope lock

- **Branch:** `main` (bootstrap commit), then `develop` created from `main`.
- **Date:** 2026-11-28

### Inspection (actual output)

| Check | Result |
|---|---|
| Working directory | `/Users/ratul/Desktop/swe/LAB 6` — contained only `LecMerge_Overnight_Agent_Build_Spec.md` |
| `git rev-parse --is-inside-work-tree` | `fatal: not a git repository` → ran `git init -b main` |
| `git remote -v` | empty → `git remote add origin https://github.com/rahulratul/LecMerge.git` |
| `git ls-remote origin` | `5734ac6… refs/heads/main` (push/read access over HTTPS OK) |
| `git fetch origin` / `git pull origin main` | pulled GitHub `Initial commit` (README.md with `# LecMerge`) |
| `gh --version` | `gh not found` — GitHub CLI not installed |
| `git --version` | 2.54.0 |
| `python3 --version` | Python 3.14.6 |
| `python3.12 --version` | Python 3.12.12 (chosen for `.venv`) |
| `uv` | present at `~/.local/bin/uv` (not used) |
| Browser | Google Chrome 158.0.8127.38; no `chromedriver` on PATH (Selenium Manager will be used) |
| Git identity | `rahulratul <2203025@student.ruet.ac.bd>` |

### Files changed

- `README.md` (environment + planned run commands)
- `docs/BUILD_LOG.md` (this file)
- `docs/DECISIONS.md` (D-001 … D-006)
- `LecMerge_Overnight_Agent_Build_Spec.md` (added to version control; Phase 0 boxes ticked)

### Decisions

See `docs/DECISIONS.md`: repo root layout (D-001), remote/history (D-002),
Python 3.12 venv (D-003), `gh` missing → `--no-ff` merges and manual PR commands (D-004),
Swagger/OpenAPI novelty UNCONFIRMED (D-005), stack lock (D-006).

### Limitations / open items

- **GitHub CLI not installed.** PR creation/merge/close cannot be performed by the agent.
  Student next action (optional, enables real PR evidence):
  `brew install gh && gh auth login`.
- **Self-directed tool confirmation pending.** Student must confirm that Swagger/OpenAPI
  was not practiced in the sessional and that the instructor accepts it.
