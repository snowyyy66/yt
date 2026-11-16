from uuid import uuid4
from fastapi.testclient import TestClient
from app.main import app
from app import storage


class Store:
    def put_object(self,*args,**kwargs):pass
    def presigned_get_object(self,bucket,key,expires):return f'https://media.test/{key}'


def auth(client):
    email=f"{uuid4().hex}@example.com"
    response=client.post('/api/auth/register',json={'email':email,'password':'long-password-123','name':'Автор'})
    return {'Authorization':f"Bearer {response.json()['access_token']}"}


def test_uploaded_video_accepts_comments_and_likes(monkeypatch):
    monkeypatch.setattr(storage,'ensure_bucket',lambda:None)
    monkeypatch.setattr(storage,'client',lambda **kwargs:Store())
    with TestClient(app) as client:
        headers=auth(client)
        upload=client.post('/api/videos',headers=headers,data={'title':'Свежий ролик'},files={'file':('movie.mp4',bytes.fromhex('00000018667479706d703432636f6e74656e74'),'video/mp4')})
        video_id=upload.json()['id']
        assert client.post(f'/api/videos/{video_id}/comments',headers=headers,json={'text':'Зашло'}).status_code==201
        assert client.put(f'/api/videos/{video_id}/like',headers=headers).json()['liked'] is True
