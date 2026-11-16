"""Populate local demonstration accounts and metadata.

Run ``python -m scripts.seed_demo`` after deployment. This creates sample users,
static-feed video metadata, and comments. The feed's video bytes are not bundled,
The demo clip is generated locally with FFmpeg and stored in MinIO.
"""

import os
import subprocess
import tempfile
from pathlib import Path

from app.media_models import VideoRecord
from app.models import Comment, SessionLocal, User
from app.security import hash_password

DEMO_USERS = (
    ("viewer@vidosphera.example.com", "Зритель", "user"),
    ("moderator@vidosphera.example.com", "Дежурный модератор", "moderator"),
    ("admin@vidosphera.example.com", "Администратор", "admin"),
    ("creator@vidosphera.example.com", "Кот Борисыч", "user"),
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


def store_demo_media(video_id: str) -> tuple[str, str]:
    from app import storage

    object_key = f"demo/{video_id}.mp4"
    thumbnail_key = f"demo/{video_id}.jpg"
    with tempfile.TemporaryDirectory() as temp_dir:
        video_path = Path(temp_dir) / "demo.mp4"
        thumbnail_path = Path(temp_dir) / "demo.jpg"
        subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "testsrc=size=640x360:rate=24", "-t", "8", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(video_path)], check=True, capture_output=True, timeout=120)
        subprocess.run(["ffmpeg", "-y", "-i", str(video_path), "-frames:v", "1", str(thumbnail_path)], check=True, capture_output=True, timeout=60)
        storage.ensure_bucket()
        with video_path.open("rb") as stream:
            storage.client().put_object(storage.bucket_name(), object_key, stream, video_path.stat().st_size, content_type="video/mp4")
        with thumbnail_path.open("rb") as stream:
            storage.client().put_object(storage.bucket_name(), thumbnail_key, stream, thumbnail_path.stat().st_size, content_type="image/jpeg")
    return object_key, thumbnail_key


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

        creator = users["creator@vidosphera.example.com"]
        video = session.get(VideoRecord, DEMO_VIDEO["id"])
        if video is None:
            video = VideoRecord(owner_id=creator.id, **DEMO_VIDEO)
            session.add(video)
            session.flush()
        if video.status != "ready":
            video.object_key, video.thumbnail_key = store_demo_media(video.id)
            video.status = "ready"

        existing = {row.text for row in session.query(Comment).filter_by(video_id=video.id).all()}
        viewer = users["viewer@vidosphera.example.com"]
        for text in DEMO_COMMENTS:
            if text not in existing:
                session.add(Comment(video_id=video.id, user_id=viewer.id, text=text))
        session.commit()

    print("Демо-данные готовы.")
    print("Демо-видео создано и сохранено в MinIO.")


if __name__ == "__main__":
    seed()
