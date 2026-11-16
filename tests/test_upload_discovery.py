from uuid import uuid4
from fastapi.testclient import TestClient
from app.main import app


def test_uploaded_public_video_appears_in_discovery_and_player(monkeypatch):
    from app import storage
    class Store:
        def put_object(self,*args,**kwargs):pass
        def presigned_get_object(self,bucket,key,expires):return f'https://media.test/{key}'
    monkeypatch.setattr(storage,'ensure_bucket',lambda:None)
    monkeypatch.setattr(storage,'client',lambda **kwargs:Store())
    with TestClient(app) as client:
        email=f"{uuid4().hex}@example.com"
        token=client.post('/api/auth/register',json={'email':email,'password':'long-password-123','name':'Автор'}).json()['access_token']
        headers={'Authorization':f'Bearer {token}'}
        upload=client.post('/api/videos',headers=headers,data={'title':'Свежее видео','visibility':'public'},files={'file':('movie.mp4',bytes.fromhex('00000018667479706d703432636f6e74656e74'),'video/mp4')})
        assert upload.status_code==201
        video_id=upload.json()['id']
        feed=client.get('/api/videos').json()
        assert any(item['id']==video_id for item in feed)
        assert client.get(f'/api/videos/{video_id}').json()['title']=='Свежее видео'
        assert client.get(f'/api/videos/{video_id}/play').json()['url'].startswith('https://media.test/')

