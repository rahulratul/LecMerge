# LecMerge — Decisions Log

This file records architecture, tooling, and scope decisions, plus any conflicts
between requirement sources. Authority order: official CSE 3206 manual →
`LecMerge_Overnight_Agent_Build_Spec.md` → existing repo conventions → agent preference.

## D-001 Repository root (Phase 0)

- The spec's Section 6.2 shows a `lecmerge/` top-level folder. The Git repository
  root is the existing workspace folder (`LAB 6/`), so the `lecmerge/` level is
  the repository root itself: `app/`, `tests/`, `docs/` sit directly at the root.
  Responsibilities are unchanged.
- The build specification file is committed at the root as the source of truth,
  so its phase checkboxes are version-controlled.

## D-002 Remote and existing history (Phase 0)

- `origin` = `https://github.com/rahulratul/LecMerge.git` (was missing; added).
- `origin/main` already held one GitHub-generated commit (`5734ac6 Initial commit`,
  `README.md` containing `# LecMerge`). It was pulled before any new work so
  later pushes are fast-forwards. No history was rewritten.

## D-003 Python environment (Phase 0)

- Default `python3` on the student's Mac is 3.14.6; `python3.12` (3.12.12) is also
  installed. The project uses a **Python 3.12 virtual environment** (`.venv`)
  because 3.12 is a mature, widely supported version for FastAPI/SQLAlchemy/Selenium
  wheels and matches what the CI runner will use.

## D-004 GitHub CLI not installed (Phase 0)

- `gh` is not installed on this machine, so real PR creation/merging/closing via
  the CLI cannot be executed by the agent. Plain `git push` over HTTPS works
  (`git ls-remote origin` succeeded).
- Consequence: feature branches are integrated into `develop` with
  `git merge --no-ff` and pushed. PR evidence (Section 10.3) will be written as
  ready-to-run commands/titles/bodies in `docs/evidence/README.md` for the student,
  unless `gh` becomes available and authenticated.

## D-005 Self-directed tool: Swagger UI / OpenAPI (Phase 0) — UNCONFIRMED

- Proposed candidate: FastAPI-generated Swagger UI / OpenAPI at `/docs`.
- **Status: not confirmed.** The agent has no record of which tools were practiced
  in the sessional. No document in this repository may describe Swagger/OpenAPI as
  "new" or "self-directed" until the student confirms it was not practiced and the
  instructor accepts it. If it was practiced, a different approved tool must be chosen.

## D-006 Stack lock (Phase 0)

- Python, FastAPI, Jinja2 (server-rendered HTML, local CSS, no JS framework),
  SQLite via SQLAlchemy, Pydantic schemas, PyTest + pytest-cov, FastAPI TestClient,
  Selenium (Selenium Manager, headless Chrome).
- CI: GitHub Actions only (no Jenkins unless the instructor requires it).
- Explicitly excluded: Docker, Redis, Celery, React, external AI APIs, frontend
  build tools, authentication, OCR, real-time features, PDF/DOCX export.

## D-007 Schema initialization without migrations (Phase 3)

- For the overnight MVP, `Base.metadata.create_all()` in `app/database.py` initializes
  the SQLite schema on startup.
- In a production deployment, Alembic migrations with versioned upgrade/downgrade scripts
  should replace `create_all()` so schema changes apply cleanly without recreating data.
- Before any production schema evolution, automated SQLite backups and `PRAGMA foreign_keys`
  verification should accompany versioned migrations to prevent data loss.
