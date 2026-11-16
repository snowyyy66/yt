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

    seed_demo.seed()
    seed_demo.seed()

    with local_sessions() as session:
        assert session.scalar(select(func.count()).select_from(User)) == 4
        video=session.get(VideoRecord,"v1")
        assert video is not None
        assert video.status == "demo"
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
    seed_demo.seed()
    with TestClient(app) as client:
        response=client.post('/api/auth/login',json={'email':'moderator@vidosphera.example.com','password':'demo-password-for-tests'})
        assert response.status_code==200
    engine.dispose()
