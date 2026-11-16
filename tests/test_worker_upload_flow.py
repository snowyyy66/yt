from uuid import uuid4

from fastapi.testclient import TestClient

from app import storage
from app.main import app
from app.models import SessionLocal
from app.media_models import VideoRecord


class FakeStorage:
    def put_object(self, *args, **kwargs): pass
    def fget_object(self, bucket, key, path):
        from pathlib import Path
        Path(path).write_bytes(b"source")
    def presigned_get_object(self, bucket, key, expires): return f"https://media.test/{key}"
    def remove_object(self, bucket, key): pass


def test_upload_waits_for_worker_before_playback_then_becomes_ready(monkeypatch, tmp_path):
    from app import jobs, worker
    queued=[]
    monkeypatch.setenv("VIDEO_WORKER_ENABLED", "true")
    monkeypatch.setattr(jobs,"enqueue",lambda video_id:queued.append(video_id))
    monkeypatch.setattr(storage,"ensure_bucket",lambda:None)
    monkeypatch.setattr(storage,"client",lambda **kwargs:FakeStorage())
    monkeypatch.setattr(worker,"client",lambda:FakeStorage())
    monkeypatch.setattr(worker,"ensure_bucket",lambda:None)
    with TestClient(app) as client:
        email=f"{uuid4().hex}@example.com"
        token=client.post('/api/auth/register',json={'email':email,'password':'long-password-123','name':'Автор'}).json()['access_token']
        headers={'Authorization':f'Bearer {token}'}
        upload=client.post('/api/videos',headers=headers,data={'title':'В очереди'},files={'file':('movie.mp4',bytes.fromhex('00000018667479706d703432636f6e74656e74'),'video/mp4')})
        assert upload.status_code==201
        video_id=upload.json()['id']
        assert upload.json()['status']=='processing'
        assert queued==[video_id]
        assert client.get(f'/api/videos/{video_id}/play',headers=headers).status_code==409
        def fake_ffmpeg(command,**kwargs):
            from pathlib import Path
            Path(command[-1]).write_bytes(b'processed')
        monkeypatch.setattr(worker.subprocess,'run',fake_ffmpeg)
        assert worker.process_video(video_id) is True
        assert client.get(f'/api/videos/{video_id}/play',headers=headers).status_code==200
        with SessionLocal() as session:
            assert session.get(VideoRecord,video_id).status=='ready'


