import os
import subprocess
import tempfile
from pathlib import Path

from redis import Redis
from sqlalchemy import select

from app.jobs import QUEUE
from app.media_models import VideoRecord
from app.models import Base, SessionLocal, engine

Base.metadata.create_all(engine)
from app.storage import bucket_name, client, ensure_bucket


def process_video(video_id: str, session_factory=SessionLocal) -> bool:
    with session_factory() as session:
        video = session.get(VideoRecord, video_id)
        if video is None:
            return False
        original_key = video.object_key
    try:
        ensure_bucket()
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "source"
            processed = Path(temp_dir) / "processed.mp4"
            thumbnail = Path(temp_dir) / "thumbnail.jpg"
            client().fget_object(bucket_name(), original_key, str(source))
            subprocess.run(["ffmpeg", "-y", "-i", str(source), "-c:v", "libx264", "-c:a", "aac", "-movflags", "+faststart", str(processed)], check=True, capture_output=True, timeout=3600)
            subprocess.run(["ffmpeg", "-y", "-ss", "00:00:00.200", "-i", str(processed), "-frames:v", "1", str(thumbnail)], check=True, capture_output=True, timeout=120)
            processed_key = f"processed/{video_id}.mp4"
            thumbnail_key = f"thumbnails/{video_id}.jpg"
            with processed.open("rb") as stream:
                client().put_object(bucket_name(), processed_key, stream, processed.stat().st_size, content_type="video/mp4")
            with thumbnail.open("rb") as stream:
                client().put_object(bucket_name(), thumbnail_key, stream, thumbnail.stat().st_size, content_type="image/jpeg")
        with session_factory() as session:
            video = session.get(VideoRecord, video_id)
            if video is None:
                return False
            video.object_key = processed_key
            video.thumbnail_key = thumbnail_key
            video.status = "ready"
            session.commit()
        try:
            client().remove_object(bucket_name(), original_key)
        except Exception:
            pass
        return True
    except Exception:
        with session_factory() as session:
            video = session.get(VideoRecord, video_id)
            if video is not None:
                video.status = "failed"
                session.commit()
        return False


def run() -> None:
    connection = Redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379/0"))
    while True:
        job = connection.blpop(QUEUE, timeout=0)
        if job:
            process_video(job[1].decode())


if __name__ == "__main__":
    run()
