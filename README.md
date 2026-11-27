# LecMerge

**Collaborative Lecture Note Organizer and Study-Sheet Compiler**  
Course: CSE 3206 — Software Engineering Sessional (22 Series), RUET  
Repository: https://github.com/rahulratul/LecMerge

## Problem

University students often collect lecture notes from several classmates that are incomplete,
duplicated, or inconsistent. Before exams, they need a straightforward way to structure a
lecture into ordered topics, attach multiple note fragments without overwriting classmates'
submissions, spot missing topics and possible formula disagreements, select a canonical
version, and export a Markdown study sheet.

## Implemented MVP features (6 functional modules)

1. **Course & Lecture Manager** — Create and browse courses and lectures with optional dates.
2. **Anchor Block Manager** — Define ordered topic/slide blocks per lecture (one topic per line).
3. **Fragment Intake** — Submit multiple text fragments under contributor display names;
   submissions are preserved and never overwritten.
4. **Coverage & Conflict Analysis** — Compute coverage (`covered_blocks / total_blocks * 100`)
   via the Composite hierarchy, flag empty blocks as `BLIND SPOT`, and surface potential
   formula conflicts (`Potential formula conflict — review required`) using a deterministic
   heuristic.
5. **Merge Workspace** — Choose a merge strategy (`Most Detailed` or `Latest Submitted`) to
   save one canonical selection while preserving all original fragments and keeping unresolved
   conflict warnings visible.
6. **Study-Sheet Export & REST API** — Compile a predictable Markdown study sheet via
   `StudySheetBuilder`, preview or download `.md`, and access all core operations through
   documented `/api/v1` endpoints and Swagger UI (`/docs`).

## Tech stack

- **Backend & GUI:** Python 3.12, FastAPI, Jinja2 (server-rendered HTML, local CSS, no JS framework)
- **Persistence:** SQLite via SQLAlchemy 2.x (`PRAGMA foreign_keys=ON`)
- **Validation & API docs:** Pydantic v2, FastAPI OpenAPI 3.1 / Swagger UI (`/docs`)
- **Testing & CI:** PyTest, pytest-cov, FastAPI TestClient, Selenium (headless Chrome via Selenium Manager), GitHub Actions

## Prerequisites

- Python 3.12 (verified on macOS with `python3.12` 3.12.12 and GitHub Actions `ubuntu-latest`)
- Google Chrome or Chromium (only required to run `tests/e2e`)

## Setup and run

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload
```

- **GUI:** http://127.0.0.1:8000/
- **Swagger UI (OpenAPI):** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

The SQLite database `lecmerge.db` is created automatically in the working directory on first
startup (override with `LECMERGE_DATABASE_URL`). It is ignored by Git.

## Tests and coverage

```bash
pytest tests/unit tests/integration -q
pytest tests/unit tests/integration --cov=app --cov-report=term-missing --cov-report=html
pytest tests/e2e -q
```

## Documentation map

- [`docs/REQUIREMENTS.md`](docs/REQUIREMENTS.md) — User stories, FR/NFR, process model, UI summary
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — Layered design, SQLite schema, Composite/Strategy/Builder patterns & rejected alternatives
- [`docs/uml/class_diagram.mmd`](docs/uml/class_diagram.mmd) — Mermaid UML class diagram
- [`docs/TESTING.md`](docs/TESTING.md) — TDD progression, mocks, Selenium scenario, real coverage output
- [`docs/DECISIONS.md`](docs/DECISIONS.md) — Architectural decisions, trade-offs, self-directed tool status
- [`docs/BUILD_LOG.md`](docs/BUILD_LOG.md) — Phase-by-phase build log with verified commands and commits
- [`docs/evidence/README.md`](docs/evidence/README.md) — Evidence index, screenshots, PR instructions, merge-conflict summary
- [`docs/REPORT_OUTLINE.md`](docs/REPORT_OUTLINE.md) — Report outline, 5-minute demo script, viva guide
- [`docs/REFLECTION_DRAFT.md`](docs/REFLECTION_DRAFT.md) — 500–700 word reflection draft for student review

## Known limitations (explicitly out of scope for MVP)

- **Formula conflict heuristic:** Only compares lines containing `=` with text on both sides
  after removing whitespace. It does not understand mathematics — it can flag compatible
  formulas in the same block and miss prose disagreements. Always requires human review.
- **No authentication or contributor verification:** Contributor names are plain display text.
- **No OCR, image uploads, AI/LLM analysis, voting, real-time sync, or PDF/DOCX export.**
- **Schema creation:** Uses `Base.metadata.create_all()` instead of Alembic migrations.
