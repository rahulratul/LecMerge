"""Integration tests for Phase 4 GUI workflow: course -> lecture -> blocks -> fragments."""

from __future__ import annotations

import re
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.database import get_session, init_db, make_engine
from app.main import app


def _make_client(tmp_path: Path):
    db_file = tmp_path / "gui.db"
    engine = make_engine(f"sqlite:///{db_file}")
    init_db(bind=engine)
    SessionFactory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def _override_session():
        session = SessionFactory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = _override_session
    return engine, TestClient(app)


def test_gui_course_lecture_block_fragment_flow(tmp_path: Path) -> None:
    engine, client = _make_client(tmp_path)
    try:
        with client:
            # 1. Dashboard empty state
            res = client.get("/")
            assert res.status_code == 200
            assert 'id="courses-empty"' in res.text

            # 2. Validation error preserves form values
            bad = client.post("/courses", data={"code": "CSE 3206", "title": "   "})
            assert bad.status_code == 422
            assert "Course title is required." in bad.text
            assert 'value="CSE 3206"' in bad.text

            # 3. Create course -> redirects to course detail
            created = client.post(
                "/courses",
                data={"code": "CSE 3206", "title": "Software Engineering"},
                follow_redirects=True,
            )
            assert created.status_code == 200
            assert "CSE 3206" in created.text
            assert "Software Engineering" in created.text
            course_url = str(created.url)
            course_id = int(re.search(r"/courses/(\d+)", course_url).group(1))

            # 4. Create lecture with two ordered blocks
            lec_res = client.post(
                f"/courses/{course_id}/lectures",
                data={
                    "title": "Lecture 1: Patterns",
                    "lecture_date": "2026-11-28",
                    "topics": "Composite Pattern\n\nStrategy Pattern\n",
                },
                follow_redirects=True,
            )
            assert lec_res.status_code == 200
            assert "Lecture 1: Patterns" in lec_res.text
            assert "Composite Pattern" in lec_res.text
            assert "Strategy Pattern" in lec_res.text
            assert "0.0%" in lec_res.text
            assert "BLIND SPOT" in lec_res.text

            block_ids = [int(m) for m in re.findall(r'href="/blocks/(\d+)"', lec_res.text)]
            # Deduplicate while preserving order
            ordered_ids = list(dict.fromkeys(block_ids))
            assert len(ordered_ids) == 2
            first_block_id = ordered_ids[0]

            # 5. Open first block and submit two fragments
            b_res = client.get(f"/blocks/{first_block_id}")
            assert b_res.status_code == 200
            assert 'id="fragment-author"' in b_res.text
            assert 'id="fragment-content"' in b_res.text
            assert 'id="fragment-submit-btn"' in b_res.text

            f1 = client.post(
                f"/blocks/{first_block_id}/fragments",
                data={"author_name": "Amina", "content": "F = ma"},
                follow_redirects=True,
            )
            assert f1.status_code == 200
            assert "Amina" in f1.text
            assert "F = ma" in f1.text

            f2 = client.post(
                f"/blocks/{first_block_id}/fragments",
                data={"author_name": "Tariq", "content": "F = m * a^2\nExtended notes"},
                follow_redirects=True,
            )
            assert f2.status_code == 200
            # Both fragments remain visible
            assert "Amina" in f2.text
            assert "Tariq" in f2.text
            assert "F = ma" in f2.text
            assert "Extended notes" in f2.text
            assert "Potential formula conflict — review required" in f2.text

            # 6. Invalid IDs return clean 404
            assert client.get("/courses/99999").status_code == 404
            assert client.get("/lectures/99999").status_code == 404
            assert client.get("/blocks/99999").status_code == 404
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
