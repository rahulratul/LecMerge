# LecMerge — Requirements and Process Model

## 1. Problem statement & intended user

Students preparing for exams often merge lecture notes gathered from multiple classmates.
LecMerge lets a student or study group using a shared local instance organize courses,
lectures, and ordered topic blocks, collect non-destructive note fragments under display
names, identify blind spots and potential formula disagreements, choose a canonical fragment,
and export a Markdown study sheet. No login or identity verification is included in the MVP.

## 2. Process model: Iterative and Incremental (Agile-Lite)

LecMerge was built in 8 gated phases (`feature/p1-*` through `feature/p7-*` integrated into
`develop`, released to `main`):
- Delivers a runnable vertical slice early (Phase 1) and tests pure domain rules before
  persistence or UI (Phase 2 TDD).
- Reduces overnight integration risk by verifying each increment with automated tests before
  moving on.
- Produces clean Git history with Conventional Commits and visible branch topology.

## 3. Core user stories

1. **Course management:** As a student, I want to create and view courses so lecture materials are organized by subject.
2. **Lecture & block management:** As a student, I want to create lectures and ordered topic blocks so contributions have a clear destination.
3. **Fragment submission:** As a contributor, I want to submit text notes under my display name without overwriting other contributions.
4. **Coverage & review:** As a study-group member, I want to see which blocks have no notes and which formula-like lines may disagree.
5. **Merge:** As a reviewer, I want to choose a merge strategy and save a canonical version while keeping all original fragments.
6. **Study-sheet export:** As an exam-preparation student, I want to compile the lecture into a Markdown study sheet that I can read or download.

## 4. Functional requirements

- **FR-01:** Create and list courses with a course code and title.
- **FR-02:** Create and view lectures under a course.
- **FR-03:** Create ordered anchor blocks under a lecture.
- **FR-04:** Add multiple text fragments to an anchor block with an author display name.
- **FR-05:** Persist all courses, lectures, blocks, fragments, and merged content in SQLite.
- **FR-06:** Calculate coverage as `covered_blocks / total_blocks * 100` (0% if no blocks).
- **FR-07:** List blocks with no fragments/merged content as blind spots (`BLIND SPOT`).
- **FR-08:** Detect potential formula conflicts using the limited `=` heuristic.
- **FR-09:** Support `Most Detailed` and `Latest Submitted` merge strategies.
- **FR-10:** Persist canonical `merged_content` while retaining all submitted fragments.
- **FR-11:** Generate a Markdown study sheet with title, coverage, ordered blocks, merged content, and unresolved conflict warnings.
- **FR-12:** Download the generated study sheet as a `.md` file.
- **FR-13:** Expose documented `/api/v1` REST endpoints for create, submit, analysis, merge, and export.
- **FR-14:** Show validation/success messages in the GUI and return clean 404 responses for invalid IDs.

## 5. Non-functional requirements

- **NFR-01 Usability:** Simple, responsive dark UI using server-rendered HTML + local CSS (no JS framework).
- **NFR-02 Maintainability:** Layered separation (Presentation → Service → Domain → Repository → SQLite).
- **NFR-03 Testability:** Pure domain logic and mocked service tests run without SQLite or network.
- **NFR-04 Reliability:** Validate blank inputs, reject empty-block merges cleanly, handle missing IDs with 404.
- **NFR-05 Extensibility:** New merge strategies register in `STRATEGIES` without changing `LecMergeService`.
- **NFR-06 Documentation:** README, architecture, UML, testing, decisions, build log, and OpenAPI `/docs`.
- **NFR-07 Portability:** Runs locally on macOS and Linux (GitHub Actions) with standard Python 3.12.

## 6. Low-fidelity UI sketch & page summary

```
+------------------------------------------------------------------+
| LecMerge                                    Courses   API docs   |
+------------------------------------------------------------------+
| Dashboard (/)                                                    |
|  [ Courses List ]                      | [ New Course Form ]     |
|  CSE 3206  Software Engineering  Open  | Code / Title / Create   |
+------------------------------------------------------------------+
        |
        v  /courses/{id}           -> Lectures list + New Lecture (topics, 1/line)
        v  /lectures/{id}          -> Coverage % | Covered/Total | Blind spots | Ordered blocks + Generate Study Sheet
        v  /blocks/{id}            -> Conflict warning | Canonical box | Fragments list | Add Fragment + Merge Workspace
        v  /lectures/{id}/study-sheet -> Metrics | Warnings | Markdown preview + Download .md
```
