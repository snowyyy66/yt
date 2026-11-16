from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint_returns_service_status():
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "yt"}


def test_openapi_schema_is_available():
    response = TestClient(app).get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["title"] == "Видосфера"

