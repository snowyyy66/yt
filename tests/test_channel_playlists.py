from uuid import uuid4
from fastapi.testclient import TestClient
from app.main import app
from app.models import SessionLocal, User
from sqlalchemy import select


def test_channel_page_exposes_its_public_playlists():
    with TestClient(app) as client:
        email=f"{uuid4().hex}@example.com"
        token=client.post('/api/auth/register',json={'email':email,'password':'long-password-123','name':'Автор канала'}).json()['access_token']
        headers={'Authorization':f'Bearer {token}'}
        playlist=client.post('/api/playlists',headers=headers,json={'title':'Лучшее','visibility':'public'}).json()
        with SessionLocal() as session:
            owner=session.scalar(select(User).where(User.email==email))
            channel_id=owner.id
        results=client.get(f'/api/channels/{channel_id}/playlists').json()
        assert any(item['id']==playlist['id'] for item in results)
