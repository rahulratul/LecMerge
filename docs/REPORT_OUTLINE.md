# LecMerge — Report Outline, Demo Script, and Viva Guide

## 1. Report structure (aligned with Section 14.1)

1. **Introduction & Problem Statement** — Fragmented classmate lecture notes; see `README.md` & `docs/REQUIREMENTS.md`.
2. **Requirements & User Stories** — 6 user stories, FR-01..FR-14, NFR-01..NFR-07 (`docs/REQUIREMENTS.md`).
3. **Process Model & Justification** — Iterative & Incremental (Agile-Lite) across 8 verified phases (`docs/REQUIREMENTS.md`, `docs/BUILD_LOG.md`).
4. **GUI Prototype & Implemented Modules** — ASCII sketch + 6 modules + screenshots in `docs/evidence/screenshots/`.
5. **Architecture, Database Design & UML** — 4-layer diagram, 4 SQLite tables (`courses`, `lectures`, `anchor_blocks`, `note_fragments`), `docs/uml/class_diagram.mmd`.
6. **Design Patterns (3 patterns, 3 categories)** — Composite (structural), Strategy (behavioral), Builder (creational) with code references and rejected alternatives (`docs/ARCHITECTURE.md`).
7. **Testing, Mocks, Selenium & Coverage** — TDD Red→Green commits, `MagicMock(spec=LecMergeRepository)`, SQLite reopen test, headless Chrome E2E, 98% measured coverage (`docs/TESTING.md`).
8. **Git Workflow, PRs, Merge Conflict & CI** — Gitflow-lite (`main`/`develop`/`feature/*`), real merge conflict in `docs/DECISIONS.md` (`docs/evidence/merge_conflict_log.txt`), `.github/workflows/ci.yml`.
9. **Self-Directed Tool / Technique** — Candidate: FastAPI OpenAPI / Swagger UI at `/docs` vs manual endpoint notes / Postman-only collections. **Student must confirm this was not taught in sessional before claiming novelty (see `docs/DECISIONS.md` D-005).**
10. **AI Assistance Disclosure, Limitations & Future Work** — Disclose agent assistance honestly, list student review/verification, and cite `README.md` limitations.

## 2. Five-minute live demo sequence (Section 11.1)

Start locally with `uvicorn app.main:app --reload`:
1. **Dashboard (`/`)**: Create course `CSE 3206 — Software Engineering Sessional`.
2. **Lecture structure (`/courses/{id}`)**: Create `Lecture 4: Design Patterns` with blocks `Composite Pattern` and `Strategy Pattern`.
3. **Fragment intake (`/blocks/{id}`)**: Submit two fragments (`Amina`: `F = ma`; `Tariq`: `F = m * a^2\nDetailed derivation...`) and show both are stored.
4. **Analysis (`/lectures/{id}`)**: Point out `50.0%` coverage, `BLIND SPOT` on block 2, and `Potential formula conflict — review required` on block 1.
5. **Merge (`/blocks/{id}`)**: Select `Most Detailed`, merge, and show canonical selection while both original fragments remain intact.
6. **Study sheet (`/lectures/{id}/study-sheet`)**: Preview Markdown (including conflict warning and blind spot placeholder) and click **Download .md**.
7. **Engineering evidence**: Open `/docs` (Swagger UI), show `pytest` + coverage output, GitHub Actions, and Git branch/conflict history at https://github.com/rahulratul/LecMerge.

## 3. Viva talking points (Section 11.2)

- **Composite (`app/domain/composite.py`)**: `AnchorBlockNode` (leaf), `LectureNode`, `CourseNode` all share `CoverageNode` (`total_blocks`, `covered_blocks`, `coverage_percent`, `find_gaps`), avoiding nested loops across routers.
- **Strategy (`app/domain/strategies.py`)**: `MostDetailedStrategy` and `LatestSubmittedStrategy` implement `MergeStrategy.select()`. Adding a new strategy only adds a subclass + `STRATEGIES` entry; `LecMergeService` does not change. Ties break deterministically by lowest fragment ID.
- **Builder (`app/domain/study_sheet.py`)**: `StudySheetBuilder` assembles optional header, coverage, warnings, and block sections into an immutable `StudySheet` cleanly outside HTTP/ORM layers.
- **Conflict heuristic (`app/domain/conflict_detector.py`)**: Compares whitespace-stripped lines containing `=` with content on both sides; flags ≥2 distinct candidates for human review. Does not understand math.
- **Mocking (`tests/unit/test_services.py`)**: Mocks `LecMergeRepository` so service logic runs without SQLite; real SQLite persistence is tested separately in `tests/integration/test_repository.py`.
- **Merge conflict (`48dc4c1`)**: `feature/conflict-doc-a` and `feature/conflict-doc-b` edited the same bullet in `docs/DECISIONS.md` (`D-007`); resolved by keeping both points and re-running tests.
