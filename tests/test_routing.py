from fastapi.testclient import TestClient
from app.main import app


def test_unknown_single_segment_page_returns_not_found():
    response=TestClient(app).get('/this-page-does-not-exist')
    assert response.status_code==404
