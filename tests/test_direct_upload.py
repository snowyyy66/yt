from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def account(client):
    response = client.post("/api/auth/register", json={
        "email": f"{uuid4().hex}@example.com",
        "password": "long-password-123",
        "name": "Uploader",
    })
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_direct_upload_is_owned_verified_and_only_ready_after_completion(monkeypatch):
    from app import storage

    class FakeObjectStore:
        size = 24

        def presigned_put_object(self, bucket, key, expires):
            self.key = key
            return f"https://objects.test/{key}?signature=ok"

        def presigned_get_object(self, bucket, key, expires):
            return f"https://objects.test/{key}"

        def stat_object(self, bucket, key):
            assert key == self.key
            return type("ObjectStat", (), {"size": self.size})()

        def get_object(self, bucket, key, offset, length):
            import io
            return io.BytesIO(bytes.fromhex("00000018667479706d703432")[:length])

    store = FakeObjectStore()
    monkeypatch.setattr(storage, "ensure_bucket", lambda: None)
    monkeypatch.setattr(storage, "client", lambda **kwargs: store)
    monkeypatch.setenv("VIDEO_WORKER_ENABLED", "false")

    with TestClient(app) as client:
        owner = account(client)
        stranger = account(client)
        started = client.post("/api/videos/upload-url", headers=owner, json={
            "title": "Direct upload", "content_type": "video/mp4", "size": 24,
            "visibility": "public",
        })
        assert started.status_code == 201
        video_id = started.json()["id"]
        assert client.get(f"/api/videos/{video_id}/play").status_code == 409
        assert client.post(f"/api/videos/{video_id}/complete", headers=stranger).status_code == 404
        completed = client.post(f"/api/videos/{video_id}/complete", headers=owner)
        assert completed.status_code == 200
        assert completed.json()["status"] == "ready"
        assert client.get(f"/api/videos/{video_id}/play").status_code == 200


def test_direct_upload_rejects_invalid_size_and_unverified_object(monkeypatch):
    from app import storage

    class FakeObjectStore:
        def presigned_put_object(self, bucket, key, expires):
            self.key = key
            return "https://objects.test/upload"
        def stat_object(self, bucket, key):
            return type("ObjectStat", (), {"size": 4})()
        def get_object(self, bucket, key, offset, length):
            import io
            return io.BytesIO(b"nope")

    monkeypatch.setattr(storage, "ensure_bucket", lambda: None)
    monkeypatch.setattr(storage, "client", lambda **kwargs: FakeObjectStore())
    with TestClient(app) as client:
        owner = account(client)
        invalid = client.post("/api/videos/upload-url", headers=owner, json={
            "title": "Too large", "content_type": "video/mp4", "size": 3 * 1024**3,
        })
        assert invalid.status_code == 413
        started = client.post("/api/videos/upload-url", headers=owner, json={
            "title": "Not a video", "content_type": "video/mp4", "size": 24,
        })
        assert started.status_code == 201
        result = client.post(f"/api/videos/{started.json()['id']}/complete", headers=owner)
        assert result.status_code == 415
