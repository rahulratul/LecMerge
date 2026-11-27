# LecMerge — Build Log

Source of truth: `LecMerge_Overnight_Agent_Build_Spec.md` (Section 12).
Remote: https://github.com/rahulratul/LecMerge

## Phase status

| Phase | Name | Branch | Status |
|---|---|---|---|
| 0 | Workspace inspection, GitHub remote setup, scope lock | `main` (bootstrap) → `develop` | complete (1 item pending student: D-005) |
| 1 | Minimal runnable project scaffold | `feature/p1-project-scaffold` | complete |
| 2 | Domain logic and three design patterns (TDD) | `feature/p2-domain-patterns` | complete |
| 3 | Database, repository, application service | `feature/p3-db-and-services` | complete |
| 4 | GUI: course, lecture, block, fragment workflow | `feature/p4-gui-workflow` | complete |
| 5 | Analysis, merge workspace, Markdown export | `feature/p5-analysis-and-merge` | complete |
| 6 | REST API and OpenAPI documentation | `feature/p6-rest-api-openapi` | complete |
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

---

## Phase 3 — Database, repository, and application service

- **Branch:** `feature/p3-db-and-services` → merged `--no-ff` into `develop`.
- **Commits:** `c146a6b feat(db): implement SQLAlchemy models, repository, and application service`;
  merge `074d415 merge: feature/p3-db-and-services into develop`.
- **Push:** `feature/p3-db-and-services` and `develop` pushed to `origin`.

### Files changed

`app/models.py`, `app/repository.py`, `app/services.py`, `tests/unit/test_services.py`,
`tests/integration/test_repository.py`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`.

### Implementation summary

- Four SQLAlchemy entities (`Course`, `Lecture`, `AnchorBlock`, `NoteFragment`) with foreign
  keys, cascade deletes, and deterministic ordering (`order_index`, `created_at, id`).
- `LecMergeRepository` ABC + `SQLiteRepository` with `selectinload` + `populate_existing=True`
  so relationship collections stay fresh inside a single session (`expire_on_commit=False`).
- `LecMergeService` orchestrating course/lecture/block CRUD, fragment intake, Composite
  coverage + conflict analysis, Strategy-based merging (preserving all fragments), and
  Builder-based Markdown study-sheet compilation.
- Mocked repository unit tests (`tests/unit/test_services.py`, 10 tests) and real SQLite
  persistence/reopen integration test (`tests/integration/test_repository.py`).

### Commands run and actual results

- Initial `pytest -q` caught a real identity-map caching bug (`1 failed, 49 passed`) where
  `block.fragments` stayed stale in the same session after `add_fragment`; fixed with
  `populate_existing=True` in `SQLiteRepository`.
- Re-ran `pytest -q` → `50 passed, 1 warning in 0.37s`.

### Limitations

- Web and REST routers are not yet wired to `LecMergeService` (Phases 4–6).

---

## Phase 4 — GUI: course, lecture, block, and fragment workflow

- **Branch:** `feature/p4-gui-workflow` → merged `--no-ff` into `develop`.
- **Commits:** `cb94310 feat(ui): add dashboard, course, lecture workspace, and fragment submission views`;
  merge `7857d5a merge: feature/p4-gui-workflow into develop`.
- **Push:** `feature/p4-gui-workflow` and `develop` pushed to `origin`.

### Files changed

`requirements.txt` (added `python-multipart==0.0.34`), `app/routers/web.py`,
`app/static/style.css`, `app/templates/dashboard.html`, `app/templates/course_detail.html`,
`app/templates/lecture_detail.html`, `app/templates/block_detail.html`, `app/templates/404.html`,
`tests/integration/test_gui_workflow.py`.

### Implementation summary

- Implemented server-rendered Jinja2 views using `LecMergeService` and POST/Redirect/GET:
  - Dashboard (`/`) with course list, empty state, and creation form.
  - Course detail (`/courses/{course_id}`) with lecture list and multiline topic block creation.
  - Lecture workspace (`/lectures/{lecture_id}`) with coverage metrics, blind-spot count,
    ordered anchor blocks, and status badges.
  - Anchor block detail (`/blocks/{block_id}`) with stable Selenium IDs (`#fragment-author`,
    `#fragment-content`, `#fragment-submit-btn`), fragment list with author & UTC timestamp,
    and potential formula conflict warning banner.
  - Clean 404 error template for invalid IDs and validation error messages that preserve form inputs.
- Styled with local CSS matching Section 5.1 palette (`#0B0D10`, `#13161C`, `#242933`, `#F3F4F6`,
  `#94A3B8`, `#F59E0B`, `#22C55E`/`#EF4444` strictly for merged/conflict, no gradients/emojis).

### Commands run and actual results

- `pytest -q` → `51 passed, 1 warning in 0.44s`.

### Limitations

- Merge action and study-sheet page/download are wired in Phase 5.

---

## Phase 5 — Analysis, merge workspace, and Markdown export

- **Branch:** `feature/p5-analysis-and-merge` → merged `--no-ff` into `develop`.
- **Commits:** `b77028e feat(merge): add GUI merge workspace, study-sheet page, and Markdown download`;
  merge `dbfdabd merge: feature/p5-analysis-and-merge into develop`.
- **Push:** `feature/p5-analysis-and-merge` and `develop` pushed to `origin` (`7857d5a..dbfdabd`).

### Files changed

`app/routers/web.py`, `app/templates/block_detail.html`, `app/templates/study_sheet.html`,
`tests/integration/test_gui_workflow.py`.

### Implementation summary

- Added Merge Workspace form on `/blocks/{block_id}` with `#merge-strategy-select`
  (`most_detailed`, `latest_submitted`) and `#merge-submit-btn` posting to `/blocks/{block_id}/merge`.
- Canonical merged content displays above original fragments; original fragments are preserved
  and potential formula-conflict warnings remain visible.
- Added `/lectures/{lecture_id}/study-sheet` (metrics, unresolved warnings, readable Markdown
  preview, download link `#study-sheet-download-link`) and `/lectures/{lecture_id}/study-sheet/download`
  serving `text/markdown; charset=utf-8` with `Content-Disposition: attachment`.
- Added integration test verifying empty-block merge rejection (422), merge persistence,
  blind-spot and conflict display, and `.md` download.

### Commands run and actual results

- `pytest -q` → `52 passed, 1 warning in 0.45s`.

### Limitations

- Versioned REST API endpoints (`/api/v1/...`) and OpenAPI schemas are added in Phase 6.

---

## Phase 6 — REST API and OpenAPI documentation

- **Branch:** `feature/p6-rest-api-openapi` → merged `--no-ff` into `develop`.
- **Commits:** `c723fee docs(api): add versioned REST API endpoints, Pydantic schemas, and OpenAPI snapshot`;
  merge `0cebcfb merge: feature/p6-rest-api-openapi into develop`.
- **Push:** `feature/p6-rest-api-openapi` and `develop` pushed to `origin` (`dbfdabd..0cebcfb`).

### Files changed

`app/schemas.py`, `app/routers/api.py`, `app/main.py`, `docs/openapi.json`,
`tests/integration/test_repository_and_api.py`.

### Implementation summary

- Implemented all 7 minimum versioned endpoints under `/api/v1/` reusing `LecMergeService`:
  - `GET /api/v1/courses`, `POST /api/v1/courses` (201)
  - `POST /api/v1/courses/{course_id}/lectures` (201)
  - `POST /api/v1/blocks/{block_id}/fragments` (201)
  - `GET /api/v1/lectures/{lecture_id}/analysis` (200)
  - `POST /api/v1/blocks/{block_id}/merge` (200)
  - `GET /api/v1/lectures/{lecture_id}/study-sheet` (200 JSON or `?download=true` Markdown attachment)
- Added Pydantic schemas with blank-string validators, tags, summaries, descriptions, examples,
  and documented 404/422 error responses.
- Generated reproducible OpenAPI 3.1.0 snapshot at `docs/openapi.json`.

### Commands run and actual results

- `pytest -q` → `54 passed, 1 warning in 0.55s` (including `/docs` and `/openapi.json` checks).
- `python -c "import json; from app.main import app; ..."` → wrote `docs/openapi.json`.

### Limitations

- Reminder (D-005): Swagger/OpenAPI novelty as a self-directed tool still requires student confirmation.
