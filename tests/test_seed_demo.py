from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from app.media_models import VideoRecord
from app.models import Base, Comment, User
from scripts import seed_demo


def test_seed_creates_demo_users_video_and_comments_idempotently(monkeypatch, tmp_path):
    engine=create_engine(f"sqlite:///{tmp_path / 'seed.db'}",connect_args={"check_same_thread":False})
    Base.metadata.create_all(engine)
    local_sessions=sessionmaker(bind=engine,expire_on_commit=False)
    monkeypatch.setattr(seed_demo,"SessionLocal",local_sessions)
    monkeypatch.setenv("DEMO_PASSWORD", "test-demo-password-2026")
    media_calls=[]
    monkeypatch.setattr(seed_demo,"store_demo_media",lambda video_id:(media_calls.append(video_id) or ("demo/v1.mp4","demo/v1.jpg")))

    seed_demo.seed()
    seed_demo.seed()

    with local_sessions() as session:
        assert session.scalar(select(func.count()).select_from(User)) == 4
        video=session.get(VideoRecord,"v1")
        assert video is not None
        assert video.status == "ready"
        assert video.object_key == "demo/v1.mp4"
        assert video.thumbnail_key == "demo/v1.jpg"
        assert media_calls == ["v1"]
        assert session.scalar(select(func.count()).select_from(Comment).where(Comment.video_id=="v1")) == 2
        assert session.scalar(select(User).where(User.role=="moderator")).email == "moderator@vidosphera.example.com"
        assert session.scalar(select(User).where(User.role=="admin")).email == "admin@vidosphera.example.com"
    engine.dispose()
from fastapi.testclient import TestClient
from app.main import app


def test_seeded_moderator_can_log_in(monkeypatch, tmp_path):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.models import Base
    from scripts import seed_demo
    engine=create_engine(f"sqlite:///{tmp_path / 'seed-login.db'}")
    Base.metadata.create_all(engine)
    sessions=sessionmaker(bind=engine,expire_on_commit=False)
    monkeypatch.setattr(seed_demo,'SessionLocal',sessions)
    monkeypatch.setattr('app.main.SessionLocal',sessions)
    monkeypatch.setenv('DEMO_PASSWORD','demo-password-for-tests')
    monkeypatch.setattr(seed_demo,'store_demo_media',lambda video_id:("demo/v1.mp4","demo/v1.jpg"))
    seed_demo.seed()
    with TestClient(app) as client:
        response=client.post('/api/auth/login',json={'email':'moderator@vidosphera.example.com','password':'demo-password-for-tests'})
        assert response.status_code==200
        creator=client.post('/api/auth/login',json={'email':'creator@vidosphera.example.com','password':'demo-password-for-tests'}).json()
        headers={'Authorization':f"Bearer {creator['access_token']}"}
        playback=client.get('/api/videos/v1/play',headers=headers)
        assert playback.status_code==200
    engine.dispose()
