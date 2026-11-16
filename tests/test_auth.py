from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def test_registration_and_login_issue_bearer_token():
    email = f"{uuid4().hex}@example.com"
    with TestClient(app) as client:
        created = client.post("/api/auth/register", json={"email":email,"password":"a-long-password","name":"Новичок"})
        assert created.status_code == 201
        token = created.json()["access_token"]
        profile = client.get("/api/auth/me", headers={"Authorization":f"Bearer {token}"})
        assert profile.status_code == 200
        assert profile.json()["name"] == "Новичок"
        signed_in = client.post("/api/auth/login", json={"email":email,"password":"a-long-password"})
        assert signed_in.status_code == 200


def test_comments_require_a_signed_in_account():
    with TestClient(app) as client:
        response = client.post("/api/videos/v1/comments", json={"text":"Классное видео"})
        assert response.status_code == 401
