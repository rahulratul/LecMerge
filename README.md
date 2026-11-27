# LecMerge

Collaborative Lecture Note Organizer and Study-Sheet Compiler — CSE 3206 Software
Engineering Sessional (22 Series), RUET.

GitHub: https://github.com/rahulratul/LecMerge

> Status: under phased construction. See `docs/BUILD_LOG.md` for verified progress.

## Environment

- Python 3.12 virtual environment (`python3.12` on macOS; see `docs/DECISIONS.md` D-003).

## Setup and run (planned commands; verified results are recorded in the build log)

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload
```

GUI: http://127.0.0.1:8000/ — API docs: http://127.0.0.1:8000/docs
