from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.main import app, db_session
from app.models import Base, User


def test_moderator_can_hide_a_reported_demo_video(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'moderation.db'}")
    Base.metadata.create_all(engine)
    sessions = sessionmaker(bind=engine, expire_on_commit=False)

    def override_db():
        with sessions() as session:
            yield session

    app.dependency_overrides[db_session] = override_db
    try:
        with TestClient(app) as client:
            email = f"{uuid4().hex}@example.com"
            registration = client.post(
                "/api/auth/register",
                json={"email": email, "password": "long-password-123", "name": "Модератор"},
            )
            headers = {"Authorization": f"Bearer {registration.json()['access_token']}"}
            with sessions() as session:
                moderator = session.scalar(select(User).where(User.email == email))
                moderator.role = "moderator"
                session.commit()

            report = client.post(
                "/api/videos/v2/reports",
                headers=headers,
                json={"reason": "Проверка скрытия демо-видео"},
            )
            assert report.status_code == 201

            hidden = client.post("/api/moderation/videos/v2/hide", headers=headers)
            assert hidden.status_code == 200
            assert hidden.json()["hidden"] is True
            assert client.get("/api/videos/v2").status_code == 404
            assert all(video["id"] != "v2" for video in client.get("/api/videos").json())
    finally:
        app.dependency_overrides.pop(db_session, None)
        engine.dispose()
