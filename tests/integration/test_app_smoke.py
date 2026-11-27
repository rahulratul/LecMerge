"""Phase 1 smoke test: the app starts and the dashboard renders."""

from fastapi.testclient import TestClient

from app.main import app


def test_dashboard_renders_with_empty_state() -> None:
    with TestClient(app) as client:
        response = client.get("/")
    assert response.status_code == 200
    assert "LecMerge" in response.text
    assert 'id="courses-empty"' in response.text


def test_static_stylesheet_is_served() -> None:
    with TestClient(app) as client:
        response = client.get("/static/style.css")
    assert response.status_code == 200
    assert "--bg: #0B0D10" in response.text
