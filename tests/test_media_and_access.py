from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.main import app
from app.models import SessionLocal, User


def account(client, name):
    email=f"{uuid4().hex}@example.com"
    result=client.post('/api/auth/register',json={'email':email,'password':'long-password-123','name':name}).json()
    return {'Authorization':f"Bearer {result['access_token']}"}, email


def test_upload_and_private_video_grant_enforce_access(monkeypatch):
    from app import storage

    class FakeObjectStore:
        def put_object(self, *args, **kwargs):
            self.object = args[1]
        def presigned_get_object(self, bucket, key, expires):
            return f"https://objects.test/{key}"

    monkeypatch.setattr(storage, 'ensure_bucket', lambda: None)
    monkeypatch.setattr(storage, 'client', lambda **kwargs: FakeObjectStore())
    with TestClient(app) as client:
        owner,_=account(client,'Автор')
        viewer,viewer_email=account(client,'Зритель')
        upload=client.post('/api/videos',headers=owner,data={'title':'Секретный ролик','visibility':'private'},files={'file':('secret.mp4',b'\x00\x00\x00\x18ftypmp42video-data','video/mp4')})
        assert upload.status_code == 201
        video_id=upload.json()['id']
        assert client.get(f'/api/videos/{video_id}/play').status_code == 401
        assert client.get(f'/api/videos/{video_id}/play',headers=viewer).status_code == 403
        grant=client.post(f'/api/videos/{video_id}/access',headers=owner,json={'email':viewer_email})
        assert grant.status_code == 201
        allowed=client.get(f'/api/videos/{video_id}/play',headers=viewer)
        assert allowed.status_code == 200
        assert allowed.json()['url'].startswith('https://objects.test/')


def test_regular_user_cannot_open_moderation_queue():
    with TestClient(app) as client:
        headers,_=account(client,'Зритель')
        assert client.get('/api/moderation/reports',headers=headers).status_code == 403


def test_user_can_subscribe_to_another_channel():
    with TestClient(app) as client:
        subscriber,_=account(client,'Подписчик')
        _,email=account(client,'Автор')
        with SessionLocal() as session:
            channel=session.scalar(select(User).where(User.email==email))
            channel_id=channel.id
        response=client.put(f'/api/channels/{channel_id}/subscribe',headers=subscriber)
        assert response.status_code == 200
        assert response.json()['subscribed'] is True

