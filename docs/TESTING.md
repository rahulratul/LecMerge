# LecMerge — Testing Strategy and Results

## 1. Test pyramid and layout

| Layer | Directory | Purpose | External dependencies |
|---|---|---|---|
| Unit (domain, TDD) | `tests/unit/test_composite.py`, `test_strategies.py`, `test_conflict_detector.py`, `test_study_sheet.py`, `test_domain_isolation.py` | Verify pure domain rules (Composite, Strategy, conflict heuristic, Builder) and enforce framework isolation | None |
| Unit (service, mocked) | `tests/unit/test_services.py` | Verify `LecMergeService` orchestration and validation without SQLite | `unittest.mock.MagicMock(spec=LecMergeRepository)` |
| Integration | `tests/integration/test_app_smoke.py`, `test_repository.py`, `test_gui_workflow.py`, `test_repository_and_api.py` | Verify SQLite persistence/reopen, HTML forms, REST `/api/v1` status codes, and `/docs` | Temporary SQLite DB (`tmp_path`), FastAPI `TestClient` |
| End-to-End (Selenium) | `tests/e2e/test_lecmerge_ui.py` | Verify the full browser workflow in headless Chrome against a live `uvicorn` process and temporary SQLite DB | Local Google Chrome + Selenium Manager |

## 2. TDD progression

Core domain modules in Phase 2 (`feature/p2-domain-patterns`) were built Red → Green → Refactor
with separate `test(...)` and `feat(...)` commits visible in `git log`:
1. Composite coverage tree (`23fe8aa` → `dd004ae`)
2. Merge strategies (`afeee67` → `1b06783`)
3. Formula conflict heuristic (`5ded625` → `3447ed6`)
4. Study-sheet builder (`2900a7e` → `64d604d`)

## 3. Mocking rationale

`tests/unit/test_services.py` mocks `LecMergeRepository` (`MagicMock(spec=LecMergeRepository)`)
so `LecMergeService` can be tested independently of SQLite I/O:
- Verifies normalization, duplicate-code checks, blank-topic filtering, fragment validation,
  strategy delegation, `save_merged_content` calls, and `NotFoundError` handling.
- Domain strategies are **not** mocked in their own unit tests (`test_strategies.py`) or in
  service tests; real domain rules execute directly.

## 4. Selenium end-to-end scenario

`tests/e2e/test_lecmerge_ui.py` starts `uvicorn app.main:app` on a free local port with a
disposable SQLite file (`LECMERGE_DATABASE_URL`), drives headless Chrome via Selenium Manager
(no hard-coded ChromeDriver path), and verifies:
1. Dashboard empty state (`#courses-empty`).
2. Creating course `CSE 3206`.
3. Creating lecture with two ordered blocks (`Composite Pattern`, `Strategy Pattern`).
4. Submitting two conflicting formula fragments (`F = ma` and `F = m * a^2\n...`) under
   different contributor names using `#fragment-author`, `#fragment-content`, `#fragment-submit-btn`.
5. Confirming both fragments remain visible and `Potential formula conflict — review required` renders.
6. Confirming lecture workspace shows `50.0%` coverage, `BLIND SPOT` for block 2, and the
   potential-conflict warning for block 1.
7. Selecting `most_detailed` in `#merge-strategy-select`, clicking `#merge-submit-btn`, and
   verifying `#canonical-content` displays while both original fragments remain visible.
8. Opening the study sheet and verifying its Markdown content and `#study-sheet-download-link`.
9. Cleanup in `finally`: quits Chrome, terminates `uvicorn`, deletes the temporary DB directory.

## 5. Exact commands and actual recorded results

```bash
pytest tests/unit tests/integration -q
pytest tests/unit tests/integration --cov=app --cov-report=term-missing --cov-report=html
pytest tests/e2e -q
```

### Actual measured coverage (macOS, Python 3.12.12, pytest 9.2.0, pytest-cov 7.1.0)

```text
Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
app/__init__.py                       0      0   100%
app/database.py                      28      0   100%
app/domain/__init__.py                0      0   100%
app/domain/composite.py              52      0   100%
app/domain/conflict_detector.py      27      0   100%
app/domain/strategies.py             41      0   100%
app/domain/study_sheet.py            62      0   100%
app/main.py                          17      0   100%
app/models.py                        41      0   100%
app/repository.py                    51      1    98%   134
app/routers/__init__.py               0      0   100%
app/routers/api.py                   64      1    98%   39
app/routers/web.py                  105     13    88%   139-144, 231-236, 264
app/schemas.py                      115      0   100%
app/services.py                     169      2    99%   184, 272
---------------------------------------------------------------
TOTAL                               772     17    98%
54 passed, 1 warning in 1.17s
```

### Actual Selenium result

```text
pytest tests/e2e -q
1 passed in 7.47s
```

## 6. Known testing limitations

- `pytest` runs with zero warnings (`httpx2==2.16.2` satisfies Starlette 1.10's `TestClient` without deprecation warnings).
- The Selenium test requires Chrome/Chromium on the host (on macOS, Google Chrome is
  installed; on GitHub Actions `ubuntu-latest`, Google Chrome is preinstalled and Selenium
  Manager resolves ChromeDriver automatically).
- The conflict heuristic is deterministic and intentionally limited; tests verify its
  documented rule, not mathematical equivalence.
