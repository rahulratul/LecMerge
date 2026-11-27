"""Integration tests for the versioned REST API (/api/v1) and OpenAPI docs."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.database import get_session, init_db, make_engine
from app.main import app


def _make_client(tmp_path: Path):
    db_file = tmp_path / "api.db"
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


def test_openapi_and_swagger_ui_load(tmp_path: Path) -> None:
    engine, client = _make_client(tmp_path)
    try:
        with client:
            docs = client.get("/docs")
            assert docs.status_code == 200
            assert "swagger-ui" in docs.text.lower()

            schema = client.get("/openapi.json")
            assert schema.status_code == 200
            paths = schema.json()["paths"]
            expected_paths = {
                "/api/v1/courses",
                "/api/v1/courses/{course_id}/lectures",
                "/api/v1/blocks/{block_id}/fragments",
                "/api/v1/lectures/{lecture_id}/analysis",
                "/api/v1/blocks/{block_id}/merge",
                "/api/v1/lectures/{lecture_id}/study-sheet",
            }
            assert expected_paths.issubset(set(paths))
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_api_end_to_end_and_error_codes(tmp_path: Path) -> None:
    engine, client = _make_client(tmp_path)
    try:
        with client:
            # List empty courses
            assert client.get("/api/v1/courses").json() == []

            # Create course (201)
            c_res = client.post("/api/v1/courses", json={"code": "cse 3206", "title": "Software Engineering"})
            assert c_res.status_code == 201
            course = c_res.json()
            assert course["code"] == "CSE 3206"

            # Duplicate course (422)
            dup = client.post("/api/v1/courses", json={"code": "CSE 3206", "title": "Duplicate"})
            assert dup.status_code == 422

            # Create lecture with ordered blocks (201)
            l_res = client.post(
                f"/api/v1/courses/{course['id']}/lectures",
                json={
                    "title": "Lecture 5: APIs",
                    "lecture_date": "2026-11-28",
                    "block_topics": ["Composite Pattern", "Strategy Pattern"],
                },
            )
            assert l_res.status_code == 201
            lecture = l_res.json()
            assert [b["topic"] for b in lecture["blocks"]] == ["Composite Pattern", "Strategy Pattern"]
            b1_id, b2_id = lecture["blocks"][0]["id"], lecture["blocks"][1]["id"]

            # Reject blank fragment (422)
            bad_frag = client.post(
                f"/api/v1/blocks/{b1_id}/fragments",
                json={"author_name": "Amina", "content": "   "},
            )
            assert bad_frag.status_code == 422

            # Submit two fragments (201)
            f1 = client.post(
                f"/api/v1/blocks/{b1_id}/fragments",
                json={"author_name": "Amina", "content": "F = ma"},
            )
            f2 = client.post(
                f"/api/v1/blocks/{b1_id}/fragments",
                json={"author_name": "Tariq", "content": "F = m * a^2\nDetailed explanation"},
            )
            assert f1.status_code == 201
            assert f2.status_code == 201

            # Analysis (200)
            ana = client.get(f"/api/v1/lectures/{lecture['id']}/analysis")
            assert ana.status_code == 200
            ana_data = ana.json()
            assert ana_data["total_blocks"] == 2
            assert ana_data["covered_blocks"] == 1
            assert ana_data["coverage_percent"] == 50.0
            assert ana_data["blind_spot_ids"] == [b2_id]
            assert ana_data["blocks"][0]["has_potential_conflict"] is True

            # Merge empty block fails cleanly (422)
            bad_merge = client.post(f"/api/v1/blocks/{b2_id}/merge", json={"strategy": "most_detailed"})
            assert bad_merge.status_code == 422

            # Merge populated block succeeds (200) and keeps all fragments
            merge = client.post(f"/api/v1/blocks/{b1_id}/merge", json={"strategy": "most_detailed"})
            assert merge.status_code == 200
            m_data = merge.json()
            assert m_data["selected_author"] == "Tariq"
            assert m_data["fragment_count"] == 2
            assert m_data["has_potential_conflict"] is True

            # Study sheet JSON (200) and Markdown download (200)
            sheet_json = client.get(f"/api/v1/lectures/{lecture['id']}/study-sheet")
            assert sheet_json.status_code == 200
            assert "Potential formula conflict — review required" in sheet_json.json()["markdown"]

            sheet_dl = client.get(f"/api/v1/lectures/{lecture['id']}/study-sheet?download=true")
            assert sheet_dl.status_code == 200
            assert "text/markdown" in sheet_dl.headers["content-type"]
            assert "# Lecture 5: APIs" in sheet_dl.text

            # 404 responses for missing IDs
            assert client.post("/api/v1/courses/999/lectures", json={"title": "X"}).status_code == 404
            assert client.post("/api/v1/blocks/999/fragments", json={"author_name": "A", "content": "B"}).status_code == 404
            assert client.post("/api/v1/blocks/999/merge", json={"strategy": "most_detailed"}).status_code == 404
            assert client.get("/api/v1/lectures/999/analysis").status_code == 404
            assert client.get("/api/v1/lectures/999/study-sheet").status_code == 404
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
