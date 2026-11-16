from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_homepage_contains_parody_brand_and_video_feed():
    response = client.get("/")

    assert response.status_code == 200
    assert "Видосфера" in response.text
    assert "Свежее из бесконечной ленты" in response.text


def test_video_api_lists_demo_videos():
    response = client.get("/api/videos")

    assert response.status_code == 200
    assert response.json()[0]["title"] == "Как я нажал «пропустить рекламу» 47 раз"
