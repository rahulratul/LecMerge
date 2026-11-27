LecMerge — Overnight Agentic Build Specification

Course: CSE 3206 – Software Engineering Sessional (22 Series), RUET

Project type: GUI-based web application with a documented REST API

Remote repository: https://github.com/rahulratul/LecMerge

Primary stack: Python, FastAPI, Jinja2, SQLite, SQLAlchemy, PyTest, Selenium

Build style: Phase-gated, incremental, test-first where practical

Deadline constraint: Overnight MVP — prioritize a complete, demonstrable vertical slice over optional sophistication.

Purpose of this document: This is the source of truth for an AI coding agent implementing LecMerge. Read it before changing or creating project files. Build one phase at a time, verify its acceptance criteria, mark it complete, update the build log, commit and push to the configured GitHub repository, and then continue automatically to the next phase. Do not skip failed phases or claim work that has not been verified.

0. Instructions for the AI coding agent

0.1 Authority and scope

Use the following order when making decisions:

The official CSE 3206 project manual supplied by the student.

This revised build specification.

Existing repository conventions and working code, provided they do not conflict with items 1 or 2.

Your own implementation preferences.

Do not silently reinterpret assignment requirements. If two requirements appear to conflict, record the conflict in docs/DECISIONS.md and choose the simplest option that preserves the official manual.

The assignment manual requires a non-trivial application following the SDLC, at least five functional modules, persistent storage, extensibility, requirements and a process model, three design patterns from at least two categories, UML, TDD, mocks, coverage evidence, Git branches/PR evidence/merge-conflict evidence, at least one genuinely self-directed tool or technique, a report, a 500–700 word reflection essay, and a short live demo/viva.

0.2 Mandatory phase protocol

Maintain the checklist in Section 12 and docs/BUILD_LOG.md.

For every phase, do the following in order:

Read the phase completely before coding.

Inspect relevant existing files and current Git branch (git status, git branch). Do not overwrite working code blindly.

Create or switch to the appropriate feature/<phase-id>-<short-name> branch off develop (after Phase 0 initializes main and develop).

Implement only the scope assigned to that phase.

Run the exact verification commands for that phase.

Inspect the output and fix failures caused by your changes.

Check that the phase acceptance criteria are all satisfied.

Update the phase checkbox in this file from [ ] to [x] only after verification succeeds.

Append to docs/BUILD_LOG.md: phase name, branch name, files changed, implementation summary, commands run, actual results, decisions, and any remaining limitations.

Create a meaningful Conventional Commit, push the branch to origin (https://github.com/rahulratul/LecMerge.git), and integrate it into develop (via GitHub PR when gh CLI is authenticated, or a non-fast-forward merge commit --no-ff followed by git push origin develop so branch history is preserved).

Continue to the next phase automatically. Do not ask the student to approve every phase.

If a phase cannot be completed safely (or if GitHub remote push/PR authentication fails):

Leave the affected checkbox unchecked and mark its status BLOCKED in docs/BUILD_LOG.md.

Record the exact error, attempted fix, and smallest next action (for example, exact git push or gh auth login commands for the student).

If only a remote GitHub push/PR step is blocked by credentials, continue local implementation and commits where safe, and clearly log the unpushed branches for the student.

Do not mark dependent phases complete and do not pretend tests or CI runs passed.

Do not fabricate screenshots, test output, coverage, CI runs, pull requests, reviews, or merge-conflict evidence.

Use these status meanings consistently:

[ ] Not completed or still in progress.

[x] Completed and verified.

BLOCKED The phase cannot safely proceed; explain why in the build log.

0.3 Anti-hallucination and implementation rules

Treat this document as a bounded specification, not permission to invent features.

Do not add features that are not in the MVP scope.

Do not invent package versions, external service credentials, API keys, or successful command results.

Do not claim that formula detection understands mathematical meaning. It uses a documented heuristic and reports potential conflicts for human review.

Do not claim that the app provides real-time collaboration, authentication, OCR, or cloud synchronization.

Do not call a tool “self-directed” unless the student confirms it was not already practiced in the sessional and it is acceptable to the instructor.

Do not fabricate a GitHub PR review, fake reviewer identity, rejected PR, merge conflict, Jenkins/GitHub Actions run, or screenshot. Execute real Git/GitHub operations against https://github.com/rahulratul/LecMerge when authenticated, and record only real command outputs and URLs.

Never force-push (git push --force) to main or develop, and never rewrite already-pushed history unless explicitly instructed by the student.

Prefer small functions, explicit names, type hints, clear error handling, and readable code over clever abstractions.

Keep domain rules independent of HTTP, HTML, and database code.

Reuse one service layer from both the GUI routes and API routes. Do not implement the same business rules twice.

Preserve submitted note fragments when merging. A merge selects a canonical version; it must not delete contributor submissions.

Use deterministic tie-breaking in merge strategies so tests are repeatable.

Avoid unnecessary JavaScript. The UI should work with ordinary HTML forms and server-rendered pages.

Do not introduce Docker, Redis, Celery, React, external AI APIs, or a frontend build system for this MVP.

Never put secrets, GitHub tokens, local database files, virtual environments, browser profiles, or generated caches into Git.

0.4 Required progress updates

At the end of each phase, write a concise progress entry to docs/BUILD_LOG.md and provide the student a short update stating:

Phase completed (or blocked).

Git branch, commit hash, and push/PR status on https://github.com/rahulratul/LecMerge.

Main files/features delivered.

Tests/commands actually run and their real result.

Next phase being started.

Do not send progress updates that merely say “working on it”.

1. Project definition

1.1 Project name

LecMerge — Collaborative Lecture Note Organizer and Study-Sheet Compiler

1.2 Problem statement

University students often collect lecture notes from several classmates. These notes may be incomplete, duplicated, or inconsistent. Before an exam, students need a simple way to organize a lecture into topics, attach multiple note contributions to each topic, identify missing topics and possible formula disagreements, choose a preferred contribution, and compile the result into a study sheet.

LecMerge provides that workflow through a lightweight browser-based GUI and a documented REST API.

1.3 Primary goal

Deliver a working, persistent, GUI-based application in which a student can:

Create a course and its lectures.

Divide each lecture into ordered topic/slide blocks.

Add multiple text fragments from different contributors to a block.

See empty blocks, lecture coverage, and potential formula conflicts.

Select a merge strategy and save a canonical version without deleting the original fragments.

Generate and download a Markdown study sheet.

1.4 Explicit non-goals for the overnight MVP

Do not implement these in the overnight version:

Login, registration, role management, or verified-contributor accounts.

OCR, image uploads, handwriting recognition, or file parsing.

AI/LLM-based semantic conflict detection.

Real-time collaboration, WebSockets, chat, notifications, or live cursors.

Upvote/downvote systems or reputation scores.

PDF export, DOCX export, or complex document styling.

Cloud deployment, payments, subscriptions, or external storage.

Multiple merge histories, branching/version graphs, or Git integration inside the product.

Complex analytics dashboards.

These can be described as future enhancements, not as completed functionality.

2. Assignment compliance map

The supplied manual is the grading authority. The previous blueprint proposed useful technologies, but it over-scoped several features and treated multiple tools as self-directed without confirming what was taught. This specification retains the core academic evidence while reducing implementation risk.

Official requirement

LecMerge implementation

Evidence to retain

At least five functional modules

Course/Lecture Manager; Anchor Block Manager; Fragment Intake; Coverage & Conflict Analysis; Merge Workspace; Study-Sheet Export

GUI screenshots, user stories, working demo

Persistent storage

SQLite database through SQLAlchemy

Database schema, persistence test, sample app run

Extensibility

Service/repository separation and replaceable merge strategies

Architecture note and Strategy tests

Three design patterns, at least two categories

Composite (structural), Strategy (behavioral), Builder (creational)

UML class diagram, code, pattern rationale and rejected alternatives

Requirements and process model

User stories, functional/non-functional requirements, low-fidelity UI sketch, iterative/incremental model

docs/REQUIREMENTS.md, report

TDD

Red → Green → Refactor for core domain behavior

Tests and meaningful test/implementation commits

Mocks

Mock the repository boundary in service unit tests

tests/unit/ and docs/TESTING.md

Coverage summary

Generate coverage report; emphasize domain logic

Actual terminal output or coverage report

Selenium

One browser-based end-to-end workflow

tests/e2e/ and actual test result/screenshot

CI

One automated CI pipeline running tests

Workflow file and real successful run on GitHub Actions

Git configuration management

Feature branches, meaningful commits, accepted PR, revised/rejected PR, real merge conflict and resolution

Actual GitHub history at https://github.com/rahulratul/LecMerge and evidence screenshots

At least one new/self-directed tool or technique

Proposed candidate: FastAPI Swagger/OpenAPI documentation at /docs

Actual use, comparison with an alternative, learning log; claim novelty only after confirming it was not taught

Report, reflection, demo and viva

Documentation and evidence prepared for final submission

docs/ and final checklist

Important coverage clarification: The supplied manual asks for a coverage summary but does not state a numeric percentage threshold. The previous blueprint's 80% target is therefore an aspirational target, not a confirmed official minimum. Do not make the build fail solely because an invented threshold was not met. Report the actual measured coverage honestly.

Self-directed-tool clarification: The files supplied do not identify the exact tools already practiced in the student's sessional classes. Swagger/OpenAPI is the proposed self-directed choice because it is already part of the project idea. Before the report claims it as “new”, the student must confirm that it was not practiced and that the instructor accepts it. If it was taught, select another genuinely new and approved option; do not claim novelty falsely.

3. Process model and project workflow

3.1 Chosen process model: Iterative and Incremental (Agile-Lite)

Justification:

LecMerge is naturally divided into small functional increments.

A working application can be demonstrated before every optional feature exists.

Each increment can be tested before the next is integrated.

The approach reduces overnight integration risk compared with implementing the entire system at once.

It supports frequent Git commits and visible progress.

3.2 Development loop

For each domain feature:

Requirement → Small design → Failing test → Minimal implementation → Passing test → Refactor → Documentation → Commit & Push

For GUI and integration features, add a browser or API acceptance test after the service behavior is stable.

3.3 MVP completion definition

The MVP is complete only when the complete demonstration scenario in Section 11 works using persistent SQLite data, the main workflow is accessible through the GUI, core tests pass, the Selenium scenario passes, the repository is pushed to https://github.com/rahulratul/LecMerge, and the CI pipeline has a real recorded result.

A page that merely looks complete but does not persist or process data is not a completed module.

4. Users, user stories, and requirements

4.1 Intended user

A student or study-group member using a shared local LecMerge instance. Contributor names are entered as display text; the overnight MVP does not authenticate or verify identities.

4.2 Core user stories

Course management: As a student, I want to create and view courses so that lecture materials are organized by subject.

Lecture and block management: As a student, I want to create lectures and ordered topic blocks so that contributions have a clear destination.

Fragment submission: As a contributor, I want to submit text notes under my display name without overwriting other contributions.

Coverage and review: As a study-group member, I want to see which blocks have no notes and which formula-like lines may disagree.

Merge: As a reviewer, I want to choose a merge strategy and save a canonical version while keeping all original fragments.

Study-sheet export: As an exam-preparation student, I want to compile the lecture into a Markdown study sheet that I can read or download.

4.3 Functional requirements

FR-01: Create and list courses with a course code and title.

FR-02: Create and view lectures under a course.

FR-03: Create ordered anchor blocks under a lecture.

FR-04: Add multiple text fragments to an anchor block with an author display name.

FR-05: Store all courses, lectures, blocks, fragments, and merged content persistently in SQLite.

FR-06: Calculate lecture coverage as:

coverage_percent = covered_blocks / total_blocks * 100

A block is covered when it has at least one non-empty fragment or a saved merged version. If there are no blocks, coverage is 0%.

FR-07: List blocks with no fragments as blind spots.

FR-08: Detect potential formula conflicts using the limited deterministic rule in Section 7.4.

FR-09: Support at least two merge strategies: Most Detailed and Latest Submitted.

FR-10: Save the selected fragment's content as the block's canonical merged content, retaining all submitted fragments.

FR-11: Generate a Markdown study sheet containing the lecture title, coverage summary, ordered blocks, merged content where available, and warnings for unresolved potential conflicts.

FR-12: Download the generated study sheet as a .md file.

FR-13: Expose documented API endpoints for the main create, submit, analysis, merge, and export operations.

FR-14: Display success and validation/error messages in the GUI. Invalid IDs must produce a clear 404 response/page rather than an unhandled server error.

4.4 Non-functional requirements

NFR-01 — Usability: The GUI must be simple, responsive, readable, and usable without a JavaScript framework.

NFR-02 — Maintainability: Separate domain logic, persistence, services, and presentation concerns.

NFR-03 — Testability: Core business rules must be testable without a real database or network.

NFR-04 — Reliability: Validate input and handle missing records and empty collections safely.

NFR-05 — Extensibility: A new merge strategy should be addable without rewriting the merge service.

NFR-06 — Documentation: Provide a usable README, architecture note, test instructions, API docs, and build log.

NFR-07 — Portability: The project should run on the student's macOS environment and a standard Python environment without paid services.

5. Minimal GUI specification

5.1 GUI technology

Use FastAPI + Jinja2 server-rendered HTML + local CSS. A browser-based GUI satisfies the GUI requirement; the project does not need a desktop GUI toolkit.

Use a clean, simple layout. A small locally stored CSS file is preferred over a frontend framework or build process. Avoid depending on external CDNs for essential styling or functionality.

UI Style Rules: Build a sharp, high-contrast dark interface inspired by Linear and GitHub—no gradients, no glassmorphism, no purple/indigo accents, no emojis, and no decorative icon badges. Use Geist for UI (14px body, 24px H1 with -0.02em tracking) and Geist Mono (12px, tabular-nums) for timestamps, diff tags, and metadata. Palette: #0B0D10 background, #13161C surfaces, 1px solid #242933 hairlines, #F3F4F6 primary text, #94A3B8 muted text, #F59E0B primary accent, with #22C55E/#EF4444 reserved strictly for merged/conflict states. Keep corners crisp (4px–6px radius), use flat 1px dividers instead of stacked drop-shadow cards, and prioritize dense, scannable layout hierarchy over decorative whitespace.

5.2 Required pages

Page 1 — Dashboard (/)

App name and short description.

List of courses.

Form to create a course (course code and title).

Link to open each course.

A clear empty state when no courses exist.

Page 2 — Course detail (/courses/{course_id})

Course code and title.

List of lectures.

Form to create a lecture.

The lecture form accepts a title and a simple multiline list of block topics (one topic per line) to minimize the number of steps.

Page 3 — Lecture workspace (/lectures/{lecture_id})

Lecture title and parent course.

Coverage percentage and covered/total block count.

Ordered anchor-block list.

Each block shows its topic, fragment count, status badge (BLIND SPOT, OPEN, POTENTIAL CONFLICT, or MERGED as appropriate), and a link to its detail view.

Link/button to generate the study sheet.

Page 4 — Anchor block detail (/blocks/{block_id})

Block topic and lecture context.

Form with stable element IDs for Selenium:

#fragment-author

#fragment-content

#fragment-submit-btn

List all submitted fragments with author and timestamp.

Display potential formula-conflict warning if the deterministic detector reports one.

Merge strategy selector #merge-strategy-select with most_detailed and latest_submitted choices.

Merge button #merge-submit-btn.

Display canonical merged content after a merge.

Page 5 — Study sheet (/lectures/{lecture_id}/study-sheet)

Render the generated Markdown as readable HTML or in a readable preformatted view.

Include a download link/button for the .md file.

Include coverage and unresolved warning information.

5.3 GUI interaction rules

Use normal HTML forms and POST/Redirect/GET where appropriate.

Preserve user-entered values on validation errors where practical.

Use clear labels, visible button text, and accessible form controls.

Give important elements stable IDs for Selenium; do not use fragile CSS selectors based only on layout.

Keep the layout responsive for a laptop-sized screen.

The GUI must call the same service methods as the REST API.

6. Architecture and repository structure

6.1 Architecture

Use a lightweight layered architecture:

Browser GUI (Jinja2)          REST API (FastAPI)
          \                    /
           \                  /
             Application Service
                     |
              Domain Logic
       Composite | Strategy | Builder
                     |
             Repository Interface
                     |
           SQLAlchemy + SQLite


Responsibilities:

Presentation: HTML templates, form handling, API request/response schemas.

Service: Orchestrates use cases and coordinates domain logic with repositories.

Domain: Coverage tree, merge strategies, conflict heuristic, study-sheet builder. No database or HTTP imports.

Infrastructure: SQLAlchemy models, database session, SQLite repository implementation.

Do not create an excessive number of abstract base classes. Use an interface where it materially supports substitution or mocking.

6.2 Recommended repository structure

Keep the codebase compact. The agent may adjust filenames slightly if the existing repository has a coherent convention, but must preserve the responsibilities.

lecmerge/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app, lifespan/startup, router mounting
│   ├── database.py              # SQLite engine, session dependency, Base
│   ├── models.py                # SQLAlchemy ORM models
│   ├── schemas.py               # Pydantic request/response schemas
│   ├── repository.py            # Repository interface + SQLite implementation
│   ├── services.py              # Shared application use cases
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── composite.py         # Composite coverage/gap calculation
│   │   ├── strategies.py        # Strategy Pattern merge rules
│   │   ├── conflict_detector.py # Limited formula heuristic
│   │   └── study_sheet.py       # Builder Pattern Markdown compilation
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── web.py               # GUI routes
│   │   └── api.py               # Versioned REST API
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── course_detail.html
│   │   ├── lecture_detail.html
│   │   ├── block_detail.html
│   │   └── study_sheet.html
│   └── static/
│       └── style.css
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_composite.py
│   │   ├── test_strategies.py
│   │   ├── test_conflict_detector.py
│   │   ├── test_study_sheet.py
│   │   └── test_services.py
│   ├── integration/
│   │   └── test_repository_and_api.py
│   └── e2e/
│       └── test_lecmerge_ui.py
├── docs/
│   ├── BUILD_LOG.md
│   ├── REQUIREMENTS.md
│   ├── ARCHITECTURE.md
│   ├── TESTING.md
│   ├── DECISIONS.md
│   ├── uml/
│   │   └── class_diagram.mmd
│   └── evidence/
│       └── README.md
├── .github/
│   └── workflows/
│       └── ci.yml
├── .gitignore
├── requirements.txt
├── pytest.ini
└── README.md


6.3 Data model

Use SQLAlchemy with SQLite. Keep the schema to four core entities.

courses

id: primary key

code: required, indexed or unique if appropriate

title: required

created_at: timestamp

lectures

id: primary key

course_id: foreign key to courses

title: required

lecture_date: optional

created_at: timestamp

anchor_blocks

id: primary key

lecture_id: foreign key to lectures

order_index: integer used to preserve display order

topic: required

merged_content: nullable text

created_at: timestamp

note_fragments

id: primary key

block_id: foreign key to anchor_blocks

author_name: required display name

content: required text

created_at: timestamp

Use appropriate relationships and foreign-key behavior. Do not add user, vote, reputation, upload, or audit tables for the MVP.

For the overnight build, Base.metadata.create_all() is acceptable for initializing a new SQLite database. Record in docs/DECISIONS.md that a migration tool would be appropriate for a production version. Ensure the SQLite file is ignored by Git.

7. Required design patterns and domain behavior

All three patterns must be implemented meaningfully. Do not merely create classes with pattern names to satisfy a checklist.

7.1 Composite Pattern — structural

File: app/domain/composite.py

Problem: Coverage and blind-spot queries should behave consistently when calculated for one anchor block, a lecture, or a course.

Minimal design:

Define a small CoverageNode interface/abstract base with operations such as total_blocks(), covered_blocks(), and find_gaps().

AnchorBlockNode is a leaf. It represents one block and reports whether it is covered.

LectureNode is a composite containing block nodes.

CourseNode is a composite containing lecture nodes.

Composite nodes aggregate the results of their children.

The service may build this small in-memory tree from repository data before calculating coverage.

Coverage rule: A block is covered if it has at least one non-empty fragment or a non-empty merged_content. Empty lectures return 0% coverage and an empty gap list.

Rejected alternative: Repeated ad-hoc nested loops and isinstance() checks in routers/services. Those spread hierarchy logic across the application and make adding another grouping level harder.

7.2 Strategy Pattern — behavioral

File: app/domain/strategies.py

Problem: A study group may prefer different submitted fragments as the canonical version.

Implement:

MergeStrategy interface with a method such as select(fragments) -> NoteFragment.

MostDetailedStrategy: selects the fragment with the greatest trimmed content length.

LatestSubmittedStrategy: selects the fragment with the latest created_at.

MergeService or the application service receives the strategy selected by the request/UI and uses it to select the canonical fragment.

Determinism: Define and test a tie-break rule, such as selecting the lowest fragment ID when primary scores are equal. Handle an empty fragment list with a clear domain exception; the UI/API should return a suitable validation response rather than a server traceback.

Important: No upvote or verified-contributor strategy is included because the MVP has no voting or authentication system.

Rejected alternative: A large if/elif block embedded in the route handler. It couples presentation to merge policy and becomes difficult to extend.

7.3 Builder Pattern — creational

File: app/domain/study_sheet.py

Problem: A study sheet contains several ordered sections and optional warning/coverage information.

Implement:

StudySheet result object containing title, sections, and warning text.

StudySheetBuilder with small fluent methods such as with_title(), add_coverage_summary(), add_block_section(), add_warnings(), and build_markdown() or build().

The builder must create a predictable Markdown document from lecture data.

Keep the builder independent of FastAPI, Jinja2, and SQLAlchemy.

Rejected alternative: A long function with many boolean arguments or a large string concatenation block in the route handler. The builder keeps document assembly separate and makes optional sections easier to control.

7.4 Conflict detection — deliberately limited heuristic

File: app/domain/conflict_detector.py

Do not attempt semantic or AI-based disagreement detection.

MVP rule:

Inspect each fragment line by line.

Consider a line a candidate formula line only if it contains an equals sign (=) and has non-whitespace content on both sides.

Normalize simple whitespace differences before comparison.

If two or more distinct normalized candidate formula lines are found in the same block, report a potential formula conflict and return the lines for human review.

If there are no formula-like lines or only one unique normalized candidate, do not report a formula conflict.

The UI wording must be “Potential formula conflict — review required”, not “incorrect formula” or “confirmed conflict”. The heuristic can miss conflicts and can flag harmless differences. Document this limitation in the README and report.

A block with no fragments is a blind spot, not a formula conflict.

7.5 Merge and persistence behavior

Merging selects one existing fragment according to the requested strategy.

Save its content to anchor_blocks.merged_content.

Preserve all note_fragments unchanged.

Show the selected strategy and canonical content in the GUI.

If a block has unresolved potential formula conflicts, preserve a warning in the study-sheet output. Merging must not silently erase the warning.

Do not call the chosen fragment “verified” or “correct”; it is only the canonical selection under the chosen rule.

8. API and Swagger/OpenAPI requirements

The browser GUI is the primary user interface. The REST API exists to expose the same use cases through typed endpoints and to demonstrate API documentation.

Use FastAPI and Pydantic schemas. Swagger UI should be reachable at /docs; ReDoc may remain at /redoc.

8.1 Minimum API endpoints

Method

Endpoint

Purpose

GET

/api/v1/courses

List courses

POST

/api/v1/courses

Create a course

POST

/api/v1/courses/{course_id}/lectures

Create a lecture and its initial ordered blocks

POST

/api/v1/blocks/{block_id}/fragments

Submit a text fragment

GET

/api/v1/lectures/{lecture_id}/analysis

Return coverage, gaps, and potential formula conflicts

POST

/api/v1/blocks/{block_id}/merge

Select and persist a canonical fragment using a chosen strategy

GET

/api/v1/lectures/{lecture_id}/study-sheet

Generate or download the Markdown study sheet

The agent may add a small read endpoint needed by the GUI, but must not create an expansive API surface.

8.2 API quality rules

Use Pydantic request and response models.

Validate required strings and reject empty fragment content.

Use clear status codes: 201 for creation, 200 for successful reads/actions, 404 for missing records, and 422 for validation errors.

Include endpoint summaries, descriptions, tags, and concise examples.

Use a consistent response format.

Keep route handlers thin; call the shared application service.

Export an OpenAPI JSON snapshot to docs/openapi.json only if it can be generated reproducibly. The live /docs page is the primary API documentation.

8.3 Proposed self-directed tool

Candidate: Swagger UI / OpenAPI through FastAPI.

Demonstrate real use by:

Opening /docs.

Inspecting the LecMerge API schemas and endpoint descriptions.

Using “Try it out” to create data and execute at least one real endpoint.

Explaining how OpenAPI documents an API contract and how it differs from manually maintained endpoint notes or a Postman-only collection.

The student must verify that this tool/technique was not already practiced in the sessional before describing it as self-directed learning. If it was practiced, choose another genuinely new, instructor-acceptable tool and revise the learning-log plan. Do not claim it is new without confirmation.

9. Testing strategy

Use pytest, pytest-cov, FastAPI TestClient, and Selenium. Test core rules before integrating the GUI.

9.1 Unit tests — TDD

Use Red → Green → Refactor for the core domain behavior.

Required test cases:

Composite

Empty block is uncovered.

Block with a fragment is covered.

Block with only merged content is covered.

Lecture with a mixture of covered and empty blocks returns correct counts and percentage.

Course aggregates multiple lectures correctly.

Empty lecture returns 0%, not division-by-zero.

Strategy

Most Detailed selects the longest trimmed content.

Latest Submitted selects the latest timestamp.

Ties follow the documented deterministic rule.

Empty fragment list raises the documented domain exception.

Conflict detector

Two distinct formula-like lines trigger a potential conflict.

Whitespace-only differences normalize to the same candidate.

No equals-sign candidate produces no potential formula conflict.

Empty fragments do not crash the detector.

Study-sheet builder

Generates the lecture title and ordered block headings.

Includes merged content when present.

Includes a visible placeholder or status for an empty block.

Includes a warning for a potential formula conflict.

Produces valid, readable Markdown for empty and non-empty lectures.

9.2 Mocking requirement

Mock the repository interface in service unit tests so the service can be tested without opening a real SQLite database.

At minimum, test:

Course/lecture/block retrieval behavior.

Fragment submission orchestration.

Merge service calling the selected strategy and asking the repository to save the canonical content.

Missing-record behavior.

Do not mock the domain strategy in the strategy's own unit test. Test real domain rules directly.

9.3 Integration tests

Use a temporary SQLite database to verify:

Course → lecture → block relationships persist.

Multiple fragments are stored without overwriting one another.

Merged content is persisted while source fragments remain available.

Essential API endpoints return the documented response/status codes.

9.4 Selenium end-to-end test

Create one stable smoke workflow in tests/e2e/test_lecmerge_ui.py:

Start the app against a temporary test database.

Open the dashboard.

Create one course.

Create one lecture with two blocks (for example, “Composite Pattern” and “Strategy Pattern”).

Open the first block and submit two formula-containing fragments with different author names and differing formula lines.

Verify both fragments remain visible.

Verify the lecture shows the second block as a blind spot and displays a potential-conflict warning for the first block.

Select Most Detailed and merge.

Verify canonical merged content is shown and both original fragments remain visible.

Open the study sheet and verify its content and download link.

Use stable IDs from Section 5.2. Use Selenium Manager where supported; do not hard-code a machine-specific ChromeDriver path. In CI, use a Linux runner with a working headless Chrome/Chromium setup.

9.5 Coverage reporting

Use pytest-cov to generate:

pytest --cov=app --cov-report=term-missing --cov-report=html


Retain the real terminal output and/or htmlcov/ report. Prioritize thorough coverage of the pure domain layer. Do not claim a percentage that the tool did not report. The supplied manual does not specify a numerical minimum; if the instructor separately specifies one, update this document and enforce that actual threshold.

10. Git, GitHub remote, CI, and project evidence

10.1 Target GitHub repository and remote setup

All project code, branches, commits, CI workflows, and documentation must be stored in:

GitHub URL: https://github.com/rahulratul/LecMerge

Remote URL (origin): https://github.com/rahulratul/LecMerge.git

During Phase 0, the coding agent must:

Check if the workspace is already a Git repository (git rev-parse --is-inside-work-tree). If not, run git init -b main.

Inspect git remote -v.

If origin is missing, add it: git remote add origin https://github.com/rahulratul/LecMerge.git.

If origin points elsewhere, do not overwrite silently; verify with git remote -v, update to https://github.com/rahulratul/LecMerge.git only if clearly unconfigured, or log the discrepancy in docs/DECISIONS.md.

Fetch the remote (git fetch origin) to inspect whether main or other branches already exist on GitHub.

If origin/main already contains initial files (such as a GitHub-generated README.md or LICENSE), pull/integrate them cleanly (git pull origin main --allow-unrelated-histories if needed) before committing new work so pushes do not get rejected.

Check GitHub CLI authentication (gh auth status) and Git push capability (git ls-remote origin).

Record the result in docs/BUILD_LOG.md.

If pushing fails due to missing credentials, log the exact error and continue local branch/commit work without fabricating push results.

10.2 Branching strategy and pushing rules

Use a clean Gitflow-lite structure on https://github.com/rahulratul/LecMerge:

main: stable submission branch (receives verified merges from develop at major milestones and final submission).

develop: primary integration branch created from main.

feature/<phase-or-issue>-<short-name>: feature branches created from develop (e.g., feature/p1-project-scaffold, feature/p2-domain-patterns, feature/p3-db-and-services, feature/p4-gui-workflow, feature/p5-analysis-and-merge, feature/p6-rest-api-openapi, feature/p7-tests-selenium-ci).

fix/<issue-id>-<short-name>: bug-fix branches created from develop.

Mandatory Git & push rules:

Use meaningful Conventional Commits:

chore(repo): initialize scaffold and repository configuration

test(domain): add coverage and gap detection cases

feat(domain): implement composite coverage tree

feat(merge): add most-detailed and latest-submitted strategies

feat(ui): add lecture workspace and fragment submission

docs(api): document LecMerge endpoints in OpenAPI

test(e2e): cover lecture-to-study-sheet workflow

For TDD phases, make separate test(...) and feat(...) commits so Red → Green progression is visible in git log.

Push main, develop, and active feature branches to origin regularly (git push -u origin <branch-name>).

Merge feature branches into develop using --no-ff (or GitHub merge commits via PR) so branch topology remains visible in git log --graph.

Do not squash away all meaningful history before evidence is captured.

Never force-push to main or develop.

10.3 Pull request evidence on GitHub

The manual requires at least one accepted/merged PR and one revised or rejected/closed PR in the real GitHub repository.

If gh CLI is installed and authenticated for rahulratul/LecMerge, the agent should execute real PR operations:

Accepted PR(s):

Push a completed feature branch (e.g., feature/p2-domain-patterns or feature/p6-rest-api-openapi) to origin.

Open a real PR into develop using gh pr create --base develop --head <branch> --title "..." --body "...".

Wait for GitHub Actions CI checks to pass (once .github/workflows/ci.yml is active), then merge with a merge commit (gh pr merge <number> --merge)—or merge develop → main via a final release PR.

Revised or Rejected/Closed PR (real, non-fabricated):

Option A (Revised PR): Open a real PR for a feature branch, add a clear self-review / checklist comment documenting a real defect or improvement found during verification (e.g., missing validation edge case, stricter typing, or formatting fix), push a follow-up fix(...) commit to the same PR branch, verify tests pass, and then merge the revised PR.

Option B (Rejected/Closed PR): Create a small experimental/alternative branch (for example, an alternative conflict-rule or layout tweak that violates MVP simplicity or fails a constraint), open a PR, document the concrete engineering reason why it was rejected in a PR comment, and close it without merging (gh pr close <number> --comment "...").

Record all real PR numbers and URLs in docs/evidence/README.md and docs/BUILD_LOG.md.

If gh CLI is not authenticated, the agent must still push the feature branches to origin (if git push works) and write the exact ready-to-paste PR titles, bodies, and gh commands into docs/evidence/README.md so the student can open/close/merge them on GitHub in two minutes.

Strict rule: Do not invent fake reviewer names or claim a second person approved a PR if no second person reviewed it.

10.4 Real merge-conflict creation and resolution

The manual requires one real Git merge conflict and a documented explanation of its resolution.

During Phase 7 or Phase 8, the agent must execute and push a real merge conflict safely on two disposable feature branches off develop (targeting a small documentation or config section such as docs/DECISIONS.md or README.md so application stability is never endangered):

Ensure develop is clean and pushed:

git checkout develop
git pull origin develop


Create branch A (feature/conflict-doc-a) from develop, edit a specific section (e.g., the "Known Limitations" or "Conflict Heuristic Notes" lines in docs/DECISIONS.md), commit, and push origin feature/conflict-doc-a.

Switch back to develop, create branch B (feature/conflict-doc-b) from the same base commit, edit the exact same lines differently (adding complementary details), commit, and push origin feature/conflict-doc-b.

Merge feature/conflict-doc-a into develop (git checkout develop && git merge --no-ff feature/conflict-doc-a) and push develop.

Attempt to merge feature/conflict-doc-b into develop (git merge --no-ff feature/conflict-doc-b). Git will produce a real merge conflict.

Capture the real terminal output (git status and git diff showing the actual <<<<<<<, =======, >>>>>>> markers) and save that real log to docs/evidence/merge_conflict_log.txt.

Resolve the conflict cleanly so both intended points are preserved, remove all conflict markers, and run the test suite (pytest tests/unit tests/integration -q) to confirm nothing broke.

Stage the resolved file, complete the merge commit (git commit -m "merge: resolve conflict between conflict-doc-a and conflict-doc-b"), and push develop to origin.

Document in docs/evidence/README.md (and docs/BUILD_LOG.md): which branches conflicted, which file/lines conflicted, what was kept, and why.

Do not manually type conflict markers into a file and claim Git produced a conflict. Keep the branch commits and merge commit in the pushed Git history on https://github.com/rahulratul/LecMerge.

10.5 CI choice

Use one CI system, not multiple systems for the same project.

Overnight default: GitHub Actions, running automatically on https://github.com/rahulratul/LecMerge. Add .github/workflows/ci.yml triggered on push (to main and develop) and pull_request (targeting main and develop) to run dependency installation, unit/integration tests, coverage report, and the headless Selenium smoke test on ubuntu-latest.

Exception: If Jenkins is specifically required by the instructor or was a required tool in the student's practiced workflow, use a Jenkinsfile instead of GitHub Actions. Do not configure both merely for decoration.

After pushing .github/workflows/ci.yml to origin, inspect the actual GitHub Actions run status (gh run list / gh run view if gh is available) and fix any CI-specific failures (such as headless Chromium flags) until a real green run is recorded. A workflow file that has never executed is configuration evidence, not a successful CI run.

10.6 Optional project board

A GitHub Projects board is useful but is not essential to the MVP unless the instructor requires it or it is selected as the self-directed tool. Do not spend overnight implementation time creating an elaborate board. A minimal board may use Backlog, In Progress, Review, and Done.

11. Demonstration scenario and viva preparation

11.1 Five-minute demo sequence

Use this sequence for the live demonstration:

Dashboard: Show the GUI and create/open a course.

Lecture structure: Show a lecture with ordered anchor blocks.

Fragment intake: Submit two contributions to one block and show that both remain stored.

Analysis: Show coverage, an empty block/blind spot, and the potential formula-conflict warning.

Merge: Choose Most Detailed, merge, and show canonical content without deleting the original fragments.

Study sheet: Generate and download the Markdown output.

Engineering evidence: Briefly show /docs, the test result, GitHub Actions CI result, and Git history/PRs on https://github.com/rahulratul/LecMerge.

11.2 Viva questions the student must be able to answer

The documentation should help the student explain:

What problem does LecMerge solve, and who is the intended user?

Why was an iterative/incremental process model selected?

Where is each of the three design patterns implemented?

Why is Composite appropriate for coverage across courses, lectures, and blocks?

How can a new merge strategy be added without changing existing strategy implementations?

Why is Builder useful for Markdown study-sheet generation?

What does the conflict detector actually check, and what are its limitations?

How does the repository abstraction make service tests easier to isolate?

Which tests are unit, integration, and end-to-end tests?

What dependency is mocked and why?

What does the coverage report measure?

How does Selenium verify a real browser workflow?

What does /docs show, and how is OpenAPI generated?

What was the actual Git merge conflict, and how was it resolved?

Which tool/technique was self-directed, what alternative was considered, and what was learned?

Where was AI assistance used, and which parts can the student personally explain?

The student must understand the delivered code. Keep explanations in comments and documentation useful for learning; do not generate unnecessarily clever code that is difficult to defend in a viva. The supplied manual explicitly allows AI tools or online code only when the student can explain every part and their use is disclosed in the report. The final report must therefore state how AI assistance was used, identify the student's own implementation/review contributions, and avoid presenting unreviewed generated code as independently authored. Git history must show the student's actual contributions.

12. Phase-by-phase implementation plan

Execution rule: Complete and verify each phase before starting the next. After marking one phase complete, commit and push to https://github.com/rahulratul/LecMerge, and continue to the next phase without waiting for additional approval. The checkboxes below are updated by the coding agent as work is verified.

Phase 0 — Workspace inspection, GitHub remote setup, and scope lock

[x] Inspect the current working directory, Git status, existing source files, Python version, and available test/browser tooling.

[x] Do not delete or overwrite existing work without inspecting it.

[x] Initialize Git on main if needed, configure origin to https://github.com/rahulratul/LecMerge.git, and sync with any existing remote commits.

[x] Verify Git push access (git ls-remote origin) and GitHub CLI auth (gh auth status if installed); log results in docs/BUILD_LOG.md.

[x] Create and push the develop branch from main.

[x] Record the chosen Python environment and exact run commands in README.md or the build log.

[ ] Check whether Swagger/OpenAPI was already practiced; do not claim it as a new tool without confirmation. — PENDING student confirmation (see docs/DECISIONS.md D-005); no novelty claim made.

[x] Create a compact docs/BUILD_LOG.md with all phases listed and current status.

[x] Record architecture or tool decisions in docs/DECISIONS.md.

Acceptance gate: Existing workspace inspected; origin points to https://github.com/rahulratul/LecMerge.git; main and develop exist (and are pushed if authenticated); scope and stack are recorded; build log exists.

Phase 1 — Minimal runnable project scaffold

[x] Branch from develop as feature/p1-project-scaffold.

[x] Create the compact folder structure from Section 6.2.

[x] Create a virtual-environment setup and requirements.txt containing only dependencies actually used.

[x] Configure FastAPI, Jinja2 templates, static CSS, and a working dashboard route.

[x] Configure SQLite and SQLAlchemy session handling.

[x] Add .gitignore for .venv/, __pycache__/, .pytest_cache/, .coverage, htmlcov/, local SQLite database files, and environment files.

[x] Create a readable starter README.md with setup and run commands.

[x] Verify that the app starts and the dashboard loads in a browser.

[x] Commit, push feature/p1-project-scaffold, and merge into develop (and push develop).

Acceptance gate: The app starts using the documented command, the dashboard renders, no database/secret/cache artifact is accidentally tracked, and the branch is pushed to origin.

Phase 2 — Domain logic and three design patterns (TDD)

[ ] Branch from develop as feature/p2-domain-patterns.

[ ] Write failing tests for Composite coverage and gap calculation (test(domain): ... commit).

[ ] Implement CoverageNode, AnchorBlockNode, LectureNode, and CourseNode with aggregation behavior (feat(domain): ... commit).

[ ] Write failing tests for MostDetailedStrategy and LatestSubmittedStrategy, including ties and empty input.

[ ] Implement the Strategy interface and concrete strategies.

[ ] Write failing tests for potential formula conflict detection and whitespace normalization.

[ ] Implement the documented heuristic and its limitations.

[ ] Write failing tests for the study-sheet Builder.

[ ] Implement StudySheet and StudySheetBuilder.

[ ] Save a Mermaid UML class diagram under docs/uml/class_diagram.mmd.

[ ] Explain each pattern and one rejected alternative in docs/ARCHITECTURE.md.

[ ] Push feature/p2-domain-patterns and integrate into develop (via GitHub PR if gh is authenticated, or --no-ff merge + push).

Acceptance gate: All domain tests pass; the three patterns are used in the real workflow; no database or FastAPI import is required by the domain modules; TDD commits are pushed to origin.

Phase 3 — Database, repository, and application service

[ ] Branch from develop as feature/p3-db-and-services.

[ ] Implement the four SQLAlchemy entities: Course, Lecture, AnchorBlock, NoteFragment.

[ ] Implement relationships and foreign keys.

[ ] Implement the repository interface and SQLite repository.

[ ] Implement shared service methods for course creation, lecture/block creation, fragment submission, analysis, merge, and study-sheet generation.

[ ] Add repository integration tests using a temporary SQLite database.

[ ] Add service unit tests using a mocked repository.

[ ] Verify that merging preserves every original fragment.

[ ] Record schema and service responsibilities in docs/ARCHITECTURE.md.

[ ] Push feature/p3-db-and-services and integrate into develop.

Acceptance gate: Persistence tests pass; service tests pass with the repository mocked; reopening a session/database does not lose persisted project data; invalid IDs are handled cleanly.

Phase 4 — GUI: course, lecture, block, and fragment workflow

[ ] Branch from develop as feature/p4-gui-workflow.

[ ] Implement the dashboard and course creation/listing.

[ ] Implement course detail and lecture creation with one block topic per line.

[ ] Implement the lecture workspace with ordered blocks and coverage display.

[ ] Implement anchor block detail and text fragment submission.

[ ] Display all saved fragments with author names and timestamps.

[ ] Add validation messages and clear empty states.

[ ] Add stable Selenium IDs from Section 5.2.

[ ] Add simple responsive styling using local CSS following Section 5.1 UI style rules.

[ ] Verify the full create-course → create-lecture → create-blocks → submit-fragment flow manually or with an initial GUI test.

[ ] Push feature/p4-gui-workflow and integrate into develop.

Acceptance gate: A user can complete the core data-entry flow through the browser; data persists after app restart; fragments do not overwrite each other.

Phase 5 — Analysis, merge workspace, and Markdown export

[ ] Branch from develop as feature/p5-analysis-and-merge.

[ ] Display covered-block counts and coverage percentage.

[ ] Display blind spots for blocks with no content.

[ ] Display potential formula conflict warnings using accurate wording.

[ ] Add the strategy selector and merge action.

[ ] Save canonical merged content without deleting fragments.

[ ] Implement the study-sheet page and .md download response.

[ ] Ensure unresolved conflict warnings are present in the generated study sheet.

[ ] Add/complete service and GUI tests for analysis, merge, and export.

[ ] Push feature/p5-analysis-and-merge and integrate into develop.

Acceptance gate: The end-to-end business workflow works from GUI input through analysis, merge, and Markdown download; all expected state is persisted.

Phase 6 — REST API and OpenAPI documentation

[ ] Branch from develop as feature/p6-rest-api-openapi.

[ ] Add Pydantic request and response schemas.

[ ] Implement the minimum API endpoints from Section 8.1.

[ ] Reuse the application service; do not duplicate business logic.

[ ] Add tags, summaries, descriptions, examples, and relevant error responses.

[ ] Verify /docs loads and endpoints can be executed through Swagger UI.

[ ] Add API integration tests for successful and invalid requests.

[ ] Save an OpenAPI snapshot only if generation is reliable and repeatable.

[ ] Push feature/p6-rest-api-openapi and integrate into develop.

Acceptance gate: /docs loads, schemas are readable, and core API operations work against the same persistent data model as the GUI.

Phase 7 — Test hardening, Selenium, GitHub CI, and Git evidence

[ ] Branch from develop as feature/p7-tests-selenium-ci.

[ ] Run the complete unit and integration test suites.

[ ] Generate the actual coverage report.

[ ] Implement the Selenium smoke scenario from Section 9.4.

[ ] Verify Selenium cleanup closes the browser and removes temporary test data.

[ ] Configure .github/workflows/ci.yml according to Section 10.5.

[ ] Push feature/p7-tests-selenium-ci and merge into develop via PR (if gh is authenticated) or --no-ff merge + push to trigger a real GitHub Actions run.

[ ] Inspect the actual GitHub Actions run result; fix flaky tests or CI environment issues without weakening assertions.

[ ] Execute the real merge-conflict scenario from Section 10.4 (feature/conflict-doc-a and feature/conflict-doc-b), capture real conflict output in docs/evidence/merge_conflict_log.txt, resolve cleanly, re-run tests, and push to origin.

[ ] Create and record the required PR evidence from Section 10.3 (at least one accepted/merged PR and one revised or rejected/closed PR, or log exact manual commands if gh is unauthenticated).

[ ] Document test commands and known limitations in docs/TESTING.md.

Acceptance gate: Unit/integration tests pass, Selenium workflow passes in a supported environment, coverage is reported honestly, real merge conflict is resolved and pushed, and at least one real GitHub Actions CI run is recorded on https://github.com/rahulratul/LecMerge.

Phase 8 — Final documentation, release merge to main, and submission readiness

[ ] Complete README.md with problem, features, stack, setup, run, test, GitHub repo link, and limitations.

[ ] Complete docs/REQUIREMENTS.md and docs/ARCHITECTURE.md.

[ ] Complete docs/TESTING.md with test types, mocks, Selenium, coverage, and commands.

[ ] Complete docs/DECISIONS.md with important trade-offs and deferred features.

[ ] Complete docs/BUILD_LOG.md with actual phase outcomes, branch/PR links, and CI run results.

[ ] Verify UML diagram matches the implemented classes.

[ ] Create docs/evidence/README.md listing required screenshots, real PR numbers/URLs, merge-conflict summary, and CI run URL.

[ ] Capture or list required screenshots: dashboard, lecture workspace, blind spot, potential conflict, merged block, study sheet, /docs, tests/coverage, CI run, Git branches/PRs/conflict.

[ ] Ensure the report outline/notes cover process model, requirements, UI mock-up, patterns and rejected alternatives, testing and mock explanation, Git evidence, tool comparison, learning log, and limitations.

[ ] Draft a 500–700 word reflection essay based on the student's real experience; leave personal learning claims for the student to verify.

[ ] Run the final verification commands from a clean terminal and record the results.

[ ] Merge verified develop into main (via final release PR if gh is authenticated, or --no-ff merge) and push main to https://github.com/rahulratul/LecMerge.

[ ] Prepare the five-minute demo using Section 11.1.

Acceptance gate: Code, documentation, tests, and demo flow are coherent; main and develop are synced and pushed to https://github.com/rahulratul/LecMerge; all claims are supported by real files or outputs; any uncompleted manual GitHub screenshot/review step is clearly listed rather than fabricated.

13. Final verification commands

The exact commands may be adapted to the student's environment, but the README must contain the commands that actually work.

Typical setup and run:

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload


Open the GUI at http://127.0.0.1:8000/ and API documentation at http://127.0.0.1:8000/docs.

Tests and coverage:

pytest tests/unit tests/integration -q
pytest --cov=app --cov-report=term-missing --cov-report=html
pytest tests/e2e -q


If Selenium needs a separate browser setup, document the exact setup. Do not state that Selenium works on a machine until it has been run successfully there.

Before final handoff (Git & GitHub verification):

git remote -v
git status --short
git branch -a
git log --oneline --graph --decorate -15


If GitHub CLI (gh) is authenticated:

gh pr list --state all --limit 10
gh run list --limit 5


Check that the local database, virtual environment, secrets, and generated cache files are not committed, and that main and develop are pushed to https://github.com/rahulratul/LecMerge.

14. Documentation deliverables

The agent must maintain these documents as the implementation evolves. Keep them accurate and concise; do not postpone all documentation until the final phase.

File

Required content

README.md

Project overview, features, stack, prerequisites, setup, run, test, demo URLs, GitHub repo link, limitations

docs/REQUIREMENTS.md

Problem statement, intended users, user stories, FR/NFR, process model, UI page summary

docs/ARCHITECTURE.md

Layered architecture, data model, service flow, design-pattern implementations, rejected alternatives

docs/TESTING.md

TDD approach, unit/integration/e2e split, mocks, Selenium scenario, coverage command and actual result

docs/DECISIONS.md

Scope cuts, technology choices, conflict heuristic limitations, known trade-offs, self-directed tool decision

docs/BUILD_LOG.md

Phase status, branches/commits/PRs, actual files changed, commands/results, blockers, next step

docs/uml/class_diagram.mmd

Mermaid class diagram that matches the actual implementation

docs/evidence/README.md

Evidence checklist, PR URLs, CI run URL, merge-conflict resolution summary, and screenshot filenames/purpose; never claim missing screenshots exist

docs/evidence/merge_conflict_log.txt

Actual terminal output of the real Git merge conflict (git status / git diff) before resolution

14.1 Report structure suggestion

Introduction and problem statement.

Requirements and user stories.

Chosen process model and justification.

GUI prototype/screenshots and implemented modules.

Architecture, database design, and UML.

Composite, Strategy, and Builder: problem solved, implementation, rejected alternative.

TDD, mocks, integration tests, Selenium, and coverage result.

Git workflow, PR evidence, merge-conflict resolution, and CI evidence.

Self-directed tool/technique: reason, actual use, comparison with an alternative, learning outcome.

Limitations, future improvements, and conclusion.

14.2 Reflection essay requirements

The supplied manual specifies 500–700 words. Base the essay on actual work performed:

What was learned and in what order.

Technical decisions and why they were made.

Real obstacles and how they were resolved.

Evaluation of documentation/tutorial resources actually used.

Honest discussion of AI assistance and the student's own contributions, as required by the manual's note on AI tools and Git history.

A realistic next skill to learn.

Do not invent struggles, resources, learning outcomes, or tool usage. The student must review and personalize the final essay before submission.

15. Known limitations and future work

These are explicitly outside the overnight MVP and may be mentioned as future work:

Authentication and contributor identity verification.

Image uploads and OCR extraction.

Better formula parsing and semantic conflict analysis.

Voting and reputation mechanisms.

PDF export and richer formatting.

Revision history and comparison between merged versions.

Collaborative editing and real-time synchronization.

Deployment and multi-user production hardening.

Do not implement these unless the MVP, tests, documentation, and required academic evidence are already complete and there is sufficient time.

16. Final instruction to the coding agent

Build the smallest complete LecMerge system that satisfies the official assignment, not the largest system imaginable.

The priority order is:

A real GUI workflow that works.

Persistent SQLite data.

Five or more clearly identifiable functional modules.

Three meaningful design patterns and a matching UML diagram.

TDD, mocked service tests, integration tests, Selenium, and honest coverage evidence.

Swagger/OpenAPI documentation and one verified self-directed tool/technique.

CI, GitHub branches/PRs/merge-conflict evidence pushed to https://github.com/rahulratul/LecMerge, and submission documentation.

Optional polish only after all the above are complete.

Never trade a working, testable, explainable MVP for optional complexity. Complete phases sequentially, tick only verified phases, log real results, push verified branches to https://github.com/rahulratul/LecMerge, and continue to the next phase automatically.