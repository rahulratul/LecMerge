# LecMerge — Architecture

## 1. Layered architecture

```
Browser GUI (Jinja2)          REST API (FastAPI)
          \                    /
             Application Service          app/services.py
                     |
              Domain Logic                app/domain/
       Composite | Strategy | Builder
                     |
             Repository Interface         app/repository.py
                     |
           SQLAlchemy + SQLite            app/models.py, app/database.py
```

- **Presentation** (`app/routers/`, `app/templates/`, `app/schemas.py`): forms, HTML, request/response models.
- **Service** (`app/services.py`): orchestrates use cases; the only place GUI and API call into.
- **Domain** (`app/domain/`): pure Python. No FastAPI, Starlette, SQLAlchemy, or Jinja2
  imports — enforced by `tests/unit/test_domain_isolation.py`.
- **Infrastructure**: ORM models, session handling, SQLite repository.

## 2. Design patterns

UML: [`docs/uml/class_diagram.mmd`](uml/class_diagram.mmd)

### 2.1 Composite — structural (`app/domain/composite.py`)

- **Problem.** Coverage and blind-spot questions are asked about a single block, a lecture,
  and a course. Each level should answer the same questions the same way.
- **Implementation.** `CoverageNode` (abstract component) declares `total_blocks()`,
  `covered_blocks()`, `find_gaps()`, and a shared `coverage_percent()` (returns 0.0 for
  zero blocks). `AnchorBlockNode` is the leaf; it is covered when any fragment is non-blank
  or merged content is non-blank. `LectureNode` and `CourseNode` are composites that sum
  their children and concatenate child gaps in order.
- **Rejected alternative.** Nested loops and `isinstance()` checks in routes/services for
  each level. That spreads hierarchy rules across the codebase and requires editing every
  caller to add a new grouping level (e.g. "semester").

### 2.2 Strategy — behavioral (`app/domain/strategies.py`)

- **Problem.** A study group may prefer different fragments as the canonical version.
- **Implementation.** `MergeStrategy.select(fragments)` returns one existing fragment.
  `MostDetailedStrategy` uses trimmed content length; `LatestSubmittedStrategy` uses
  `created_at`. Ties go to the lowest fragment id (deterministic). An empty list raises
  `EmptyFragmentListError`. Strategies are registered in `STRATEGIES` and looked up with
  `get_strategy(key)`. Fragments are typed by the `FragmentLike` protocol, so ORM rows
  and test dataclasses both work without the domain importing the ORM.
- **Extending.** Add a subclass, register it in `STRATEGIES`; the service is unchanged.
- **Rejected alternative.** An `if/elif` block on the strategy name inside the route
  handler. It couples presentation to merge policy and duplicates logic between GUI and API.

### 2.3 Builder — creational (`app/domain/study_sheet.py`)

- **Problem.** A study sheet has a title, an optional course label, a coverage summary,
  optional warnings, and an ordered list of block sections whose body depends on state
  (merged / open / blind spot / potential conflict).
- **Implementation.** `StudySheetBuilder` exposes fluent steps (`with_title`,
  `add_coverage_summary`, `add_block_section`, `add_warnings`) and `build()` returns an
  immutable `StudySheet` whose `to_markdown()` produces predictable Markdown. Conflict
  warnings are attached to the block section *and* listed in a Warnings section, and are
  kept even when the block has merged content.
- **Rejected alternative.** One long function with many boolean flags, or string
  concatenation in the route handler. Optional sections become hard to control and test.

### 2.4 Conflict heuristic (`app/domain/conflict_detector.py`)

Not a design pattern; a deliberately limited rule. A line is a candidate when it has `=`
with text on both sides of the first `=`. Candidates are compared with all whitespace
removed; two or more distinct candidates in one block produce the UI text
"Potential formula conflict — review required". It does not understand mathematics, can
flag compatible formulas, and can miss disagreements written without `=`.

## 3. Data model (`app/models.py`)

Four SQLAlchemy tables in SQLite with `PRAGMA foreign_keys=ON` and `CASCADE` deletes:

| Table | Key columns | Relationships |
|---|---|---|
| `courses` | `id`, `code` (unique, indexed), `title`, `created_at` | 1:N `lectures` |
| `lectures` | `id`, `course_id` (FK), `title`, `lecture_date` (optional), `created_at` | N:1 `course`, 1:N `blocks` (ordered by `order_index`) |
| `anchor_blocks` | `id`, `lecture_id` (FK), `order_index`, `topic`, `merged_content` (nullable), `created_at` | N:1 `lecture`, 1:N `fragments` (ordered by `created_at, id`) |
| `note_fragments` | `id`, `block_id` (FK), `author_name`, `content`, `created_at` | N:1 `block` |

## 4. Repository & application service (`app/repository.py`, `app/services.py`)

- `LecMergeRepository` defines the persistence contract; `SQLiteRepository` implements it
  with SQLAlchemy `selectinload` queries so relationships are loaded deterministically.
- `LecMergeService` is the single orchestration layer called by both GUI (`app/routers/web.py`)
  and REST API (`app/routers/api.py`):
  - Course CRUD (`list_courses`, `create_course`, `get_course`, `get_course_coverage`)
  - Lecture/block creation & lookup (`create_lecture`, `get_lecture`, `get_block`)
  - Fragment intake (`submit_fragment`)
  - Analysis (`analyze_lecture`, `analyze_block_entity`) combining Composite + conflict heuristic
  - Merge (`merge_block`) applying Strategy and persisting `merged_content` while keeping all
    original `note_fragments` intact
  - Study-sheet compilation (`generate_study_sheet`) via `StudySheetBuilder`
- Raises domain/application exceptions (`NotFoundError`, `ValidationError`) so routers map
  them cleanly to 404 or 422/form validation messages.
