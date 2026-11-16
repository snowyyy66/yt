"""Populate local demonstration accounts and metadata.

Run ``python -m scripts.seed_demo`` after deployment. This creates sample users,
static-feed video metadata, and comments. The feed's video bytes are not bundled,
so seeded entries are metadata examples and cannot be played from MinIO.
"""

import os

from app.media_models import VideoRecord
from app.models import Comment, SessionLocal, User
from app.security import hash_password

DEMO_USERS = (
    ("viewer@vidosphera.test", "Зритель", "user"),
    ("moderator@vidosphera.test", "Дежурный модератор", "moderator"),
    ("admin@vidosphera.test", "Администратор", "admin"),
    ("creator@vidosphera.test", "Кот Борисыч", "user"),
)
DEMO_VIDEO = {
    "id": "v1",
    "title": "Как я нажал «пропустить рекламу» 47 раз",
    "description": "Образец метаданных для демонстрационной ленты.",
    "object_key": "demo/v1.mp4",
    "visibility": "public",
    "status": "demo",
}
DEMO_COMMENTS = (
    "Пришёл за лайфхаком, остался из-за рекламы.",
    "Алгоритм, я это уже смотрел. Но ладно.",
)


def seed() -> None:
    password = os.getenv("DEMO_PASSWORD")
    if not password or len(password) < 12:
        raise ValueError("Set DEMO_PASSWORD to a value of at least 12 characters.")

    with SessionLocal() as session:
        users = {}
        for email, name, role in DEMO_USERS:
            user = session.query(User).filter_by(email=email).one_or_none()
            if user is None:
                user = User(email=email, name=name, role=role, password_hash=hash_password(password))
                session.add(user)
                session.flush()
            elif user.role != role:
                user.role = role
            users[email] = user

        creator = users["creator@vidosphera.test"]
        video = session.get(VideoRecord, DEMO_VIDEO["id"])
        if video is None:
            video = VideoRecord(owner_id=creator.id, **DEMO_VIDEO)
            session.add(video)
            session.flush()

        existing = {row.text for row in session.query(Comment).filter_by(video_id=video.id).all()}
        viewer = users["viewer@vidosphera.test"]
        for text in DEMO_COMMENTS:
            if text not in existing:
                session.add(Comment(video_id=video.id, user_id=viewer.id, text=text))
        session.commit()

    print("Демо-данные готовы.")
    print("Ролики имеют только метаданные: видеофайлы для MinIO не добавлены.")


if __name__ == "__main__":
    seed()
