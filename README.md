# LecMerge

Collaborative Lecture Note Organizer and Study-Sheet Compiler — CSE 3206 Software
Engineering Sessional (22 Series), RUET.

GitHub: https://github.com/rahulratul/LecMerge

> Status: under phased construction. See `docs/BUILD_LOG.md` for verified progress.

## Stack

Python 3.12 · FastAPI · Jinja2 (server-rendered HTML, local CSS) · SQLite via SQLAlchemy · PyTest

## Setup (macOS, verified in Phase 1)

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

`python3.12` is used because the default `python3` on the development Mac is 3.14
(see `docs/DECISIONS.md` D-003). Any Python 3.12 interpreter works.

## Run

```bash
uvicorn app.main:app --reload
```

- GUI: http://127.0.0.1:8000/
- API docs (Swagger UI): http://127.0.0.1:8000/docs

The SQLite database file `lecmerge.db` is created in the working directory on first
start (override with `LECMERGE_DATABASE_URL`, e.g. `sqlite:////tmp/other.db`). It is
ignored by Git.

## Test

```bash
pytest -q
```

## Project layout

```
app/            FastAPI app (main.py, database.py, models, services, domain/, routers/, templates/, static/)
tests/          unit/, integration/, e2e/
docs/           BUILD_LOG, DECISIONS, and (later) REQUIREMENTS, ARCHITECTURE, TESTING, UML, evidence
```
