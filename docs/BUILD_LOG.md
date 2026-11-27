# LecMerge — Build Log

Source of truth: `LecMerge_Overnight_Agent_Build_Spec.md` (Section 12).
Remote: https://github.com/rahulratul/LecMerge

## Phase status

| Phase | Name | Branch | Status |
|---|---|---|---|
| 0 | Workspace inspection, GitHub remote setup, scope lock | `main` (bootstrap) → `develop` | complete (1 item pending student: D-005) |
| 1 | Minimal runnable project scaffold | `feature/p1-project-scaffold` | complete |
| 2 | Domain logic and three design patterns (TDD) | `feature/p2-domain-patterns` | complete |
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

### Git results (actual)

- `git commit` on `main`: `ba8d455 chore(repo): add build spec, decisions log, and build log for phase 0`
- `git push -u origin main`: `5734ac6..ba8d455  main -> main`
- `git checkout -b develop` + `git push -u origin develop`: `* [new branch]  develop -> develop`
- `git branch -a`: `develop`, `main`, `remotes/origin/develop`, `remotes/origin/main`

### Acceptance gate

- Workspace inspected: yes. `origin` → `https://github.com/rahulratul/LecMerge.git`: yes.
- `main` and `develop` exist locally and on origin: yes. Scope/stack recorded (DECISIONS D-006): yes.
- Build log exists: yes. **Phase 0 passed.** The Swagger-novelty checkbox stays unchecked
  pending student confirmation; it does not block the gate.

### Limitations / open items

- **GitHub CLI not installed.** PR creation/merge/close cannot be performed by the agent.
  Student next action (optional, enables real PR evidence):
  `brew install gh && gh auth login`.
- **Self-directed tool confirmation pending.** Student must confirm that Swagger/OpenAPI
  was not practiced in the sessional and that the instructor accepts it.

---

## Phase 1 — Minimal runnable project scaffold

- **Branch:** `feature/p1-project-scaffold` → merged `--no-ff` into `develop`.
- **Commits:** `c82995c chore(repo): initialize scaffold and repository configuration`;
  merge `19b8a9c merge: feature/p1-project-scaffold into develop`.
- **Push:** `* [new branch] feature/p1-project-scaffold`, `ba8d455..19b8a9c develop -> develop`.

### Files changed

`.gitignore`, `requirements.txt`, `pytest.ini`, `README.md`, `app/__init__.py`, `app/main.py`,
`app/database.py`, `app/models.py` (placeholder), `app/domain/__init__.py`, `app/routers/__init__.py`,
`app/routers/web.py`, `app/templates/base.html`, `app/templates/dashboard.html`, `app/static/style.css`,
`tests/conftest.py`, `tests/integration/test_app_smoke.py`, `docs/evidence/README.md`.

### Implementation summary

- FastAPI app with lifespan that calls `init_db()` (`Base.metadata.create_all`).
- SQLAlchemy engine/session (`app/database.py`), SQLite foreign keys enabled via `PRAGMA`,
  DB URL overridable through `LECMERGE_DATABASE_URL` (tests use a temp file).
- Jinja2 dashboard route `/` with empty state; local CSS with the Section 5.1 palette variables.
- `requirements.txt` lists only packages used so far (pinned to the versions pip actually installed).

### Commands run and actual results

- `python3.12 -m venv .venv` → Python 3.12.12.
- `pip install fastapi "uvicorn[standard]" jinja2 sqlalchemy python-multipart pytest pytest-cov httpx selenium`
  → installed fastapi 0.165.0, uvicorn 0.54.0, jinja2 3.1.6, sqlalchemy 2.1.9, pytest 9.2.0,
  httpx 0.29.0, selenium 4.54.0, pytest-cov 7.1.0, python-multipart 0.0.34 (latter three not yet
  in requirements.txt; added in the phase that uses them).
- `pytest -q` → `2 passed, 1 warning` (warning: Starlette deprecation notice about `httpx` in TestClient).
- `uvicorn app.main:app --port 8000` → `Application startup complete`.
- Headless Chrome via Selenium Manager loaded `http://127.0.0.1:8000/` →
  `TITLE: LecMerge`, body contained "No courses yet." (screenshot kept in agent scratch, not committed).
- `git check-ignore -v lecmerge.db .venv` → both ignored; `git status --short` showed no DB/cache files staged.

### Limitations

- Dashboard has no create form yet (Phase 4). The Starlette `httpx` deprecation warning is harmless for now.

---

## Phase 2 — Domain logic and three design patterns (TDD)

- **Branch:** `feature/p2-domain-patterns` → merged `--no-ff` into `develop`.
- **Commits (Red → Green → Refactor):**
  - `23fe8aa test(domain): add coverage and gap detection cases`
  - `dd004ae feat(domain): implement composite coverage tree`
  - `afeee67 test(merge): add strategy selection, tie-break, and empty-input cases`
  - `1b06783 feat(merge): add most-detailed and latest-submitted strategies`
  - `5ded625 test(domain): add potential formula conflict detection cases`
  - `3447ed6 feat(domain): implement limited formula conflict heuristic`
  - `2900a7e test(export): add study-sheet builder cases`
  - `64d604d feat(export): implement study-sheet builder`
  - `2e05c0b docs(domain): add UML class diagram, architecture notes, and domain isolation test`
  - `refactor(domain): make composite base class public to match UML`
  - merge `c52cb59 merge: feature/p2-domain-patterns into develop`
- **Push:** `* [new branch] feature/p2-domain-patterns`, `19b8a9c..c52cb59 develop -> develop`.

### Files changed

`app/domain/composite.py`, `app/domain/strategies.py`, `app/domain/conflict_detector.py`,
`app/domain/study_sheet.py`, `tests/unit/test_composite.py`, `tests/unit/test_strategies.py`,
`tests/unit/test_conflict_detector.py`, `tests/unit/test_study_sheet.py`,
`tests/unit/test_domain_isolation.py`, `docs/uml/class_diagram.mmd`, `docs/ARCHITECTURE.md`.

### Implementation summary

- **Composite (`app/domain/composite.py`)**: `CoverageNode`, `AnchorBlockNode`, `CompositeNode`,
  `LectureNode`, `CourseNode`. Uniform `total_blocks()`, `covered_blocks()`, `coverage_percent()`,
  and `find_gaps()`.
- **Strategy (`app/domain/strategies.py`)**: `MergeStrategy`, `MostDetailedStrategy`,
  `LatestSubmittedStrategy`, `FragmentLike` protocol, deterministic lowest-ID tie-breaking,
  `EmptyFragmentListError`, `UnknownStrategyError`, and `STRATEGIES` registry.
- **Conflict heuristic (`app/domain/conflict_detector.py`)**: line-by-line `=` candidate
  extraction, whitespace normalization, cautious warning wording (`CONFLICT_WARNING`).
- **Builder (`app/domain/study_sheet.py`)**: `StudySheet` and fluent `StudySheetBuilder`
  producing predictable Markdown with coverage, warnings, and ordered block sections.
- **Architecture guard**: AST-based `test_domain_isolation.py` verifies `app/domain/` does not
  import FastAPI, Starlette, SQLAlchemy, or Jinja2.

### Commands run and actual results

- Red phase runs for each module failed with `ModuleNotFoundError` before implementation.
- Final `pytest -q` → `39 passed, 1 warning in 0.29s`.
- `git push -u origin feature/p2-domain-patterns develop` → succeeded.

### Limitations

- Domain modules are not yet wired into persistence/services (Phase 3).
