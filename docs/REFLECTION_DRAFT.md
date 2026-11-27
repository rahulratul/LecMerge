# LecMerge — Reflection Essay Draft (500–700 words)

> **Note for student:** Review, edit, and personalize this draft before submission. Do not
> submit any learning claim that you have not personally verified or cannot defend in the viva.
> Confirm D-005 (Swagger/OpenAPI novelty) before keeping the OpenAPI paragraph as a self-directed tool.

Building LecMerge for CSE 3206 turned software engineering concepts that previously felt
separate—process models, design patterns, testing, and Git configuration management—into one
connected workflow. The core goal was deliberately focused: organize lecture notes collected
from classmates into ordered topic blocks, highlight uncovered blind spots and potential
formula disagreements, pick a canonical note without deleting anyone's submission, and compile
a downloadable Markdown study sheet.

I followed an iterative and incremental build sequence across eight gated phases rather than
coding everything at once. Starting with a minimal runnable FastAPI and Jinja2 scaffold in
Phase 1 established a working vertical slice immediately. In Phase 2, implementing the pure
domain layer test-first (Red → Green → Refactor) forced me to design clean boundaries before
writing a single SQLAlchemy model or HTML template. Adding an AST-based domain isolation test
(`tests/unit/test_domain_isolation.py`) guaranteed that Composite, Strategy, Builder, and the
conflict heuristic stayed completely free of FastAPI and database imports.

Three technical decisions shaped the codebase most strongly. First, using the Composite
pattern (`CoverageNode`, `AnchorBlockNode`, `LectureNode`, `CourseNode`) unified coverage and
blind-spot queries across every hierarchy level instead of duplicating loops in routes.
Second, placing `MergeStrategy` behind a small `FragmentLike` protocol let both SQLAlchemy
rows and plain test dataclasses pass through `MostDetailedStrategy` and
`LatestSubmittedStrategy` with deterministic lowest-ID tie-breaking. Third, separating
`LecMergeRepository` from `LecMergeService` allowed service unit tests to mock persistence
with `MagicMock(spec=LecMergeRepository)` while a shared service layer served both the
browser GUI and the versioned `/api/v1` REST API.

Several real obstacles came up during verification. During Phase 3 integration testing,
`SQLiteRepository` initially returned an empty `block.fragments` list right after inserting
two fragments in the same session because SQLAlchemy's `expire_on_commit=False` kept the
previously loaded collection cached in the identity map. Passing `populate_existing=True` on
relationship-loading queries fixed the bug cleanly. On macOS, the default `python3` was 3.14,
so locking the virtual environment and GitHub Actions workflow to Python 3.12 avoided wheel
compatibility surprises. Finally, deliberately creating a real merge conflict between
`feature/conflict-doc-a` and `feature/conflict-doc-b` on `docs/DECISIONS.md` and resolving
the `<<<<<<<` markers while re-running the test suite made Git conflict resolution concrete.

*[STUDENT TO REVIEW/PERSONALIZE: Confirm which official docs/tutorials you personally read,
such as FastAPI, SQLAlchemy 2.0, PyTest, and Selenium documentation, and confirm whether
FastAPI's automatic OpenAPI/Swagger UI at `/docs` was new to you and approved as your
self-directed tool.]* Exploring FastAPI's auto-generated OpenAPI schema at `/docs` showed how
keeping request/response contracts in Pydantic models avoids the drift common in hand-written
endpoint notes or manually maintained Postman collections.

AI coding assistance was used to accelerate scaffolding, test generation, and documentation
under a strict phase-gated specification (`LecMerge_Overnight_Agent_Build_Spec.md`). Every
phase was verified with real local commands—54 unit and integration tests reaching 98%
coverage and a headless Chrome Selenium smoke test—rather than accepting unverified output.
*[STUDENT TO REVIEW/PERSONALIZE: Describe which modules you reviewed line by line, any manual
edits you made, and how you tested the app before the viva.]*

As a realistic next step, I want to learn Alembic database migrations and proper user
authentication so a future version of LecMerge can safely evolve its schema and attribute
submissions to verified accounts rather than plain display names.
