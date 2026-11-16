from pathlib import Path
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.media_models import VideoRecord
from app.models import Base, User
from app.worker import process_video


def fixture_db(path):
    engine=create_engine(f"sqlite:///{path}",connect_args={"check_same_thread":False})
    Base.metadata.create_all(engine)
    sessions=sessionmaker(bind=engine,expire_on_commit=False)
    with sessions() as session:
        user=User(email="worker@example.com",name="worker",password_hash="unused")
        session.add(user);session.flush()
        session.add(VideoRecord(id="worker-video",owner_id=user.id,title="worker",object_key="original/worker-video",visibility="public",status="processing"))
        session.commit()
    return engine,sessions


class FakeStorage:
    def fget_object(self,bucket,key,path):Path(path).write_bytes(b"input")
    def put_object(self,bucket,key,stream,size,content_type):pass
    def remove_object(self,bucket,key):pass


def test_worker_stores_processed_video_and_marks_ready(tmp_path,monkeypatch):
    import app.worker as worker
    engine,sessions=fixture_db(tmp_path/'worker.db')
    monkeypatch.setattr(worker,"client",lambda:FakeStorage())
    monkeypatch.setattr(worker,"ensure_bucket",lambda:None)
    def fake_ffmpeg(command,**kwargs):
        Path(command[-1]).write_bytes(b"processed")
    monkeypatch.setattr(worker.subprocess,"run",fake_ffmpeg)
    assert process_video("worker-video",sessions) is True
    with sessions() as session:
        video=session.get(VideoRecord,"worker-video")
        assert video.status=="ready"
        assert video.object_key=="processed/worker-video.mp4"
        assert video.thumbnail_key=="thumbnails/worker-video.jpg"
    engine.dispose()
