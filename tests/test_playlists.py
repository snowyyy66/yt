from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def auth(client):
    email=f"{uuid4().hex}@example.com"
    result=client.post('/api/auth/register',json={'email':email,'password':'long-password-123','name':'Автор'})
    return {'Authorization':f"Bearer {result.json()['access_token']}"}


def test_private_playlist_cannot_be_read_by_another_account():
    with TestClient(app) as client:
        owner=auth(client)
        viewer=auth(client)
        created=client.post('/api/playlists',headers=owner,json={'title':'На потом','visibility':'private'})
        assert created.status_code == 201
        playlist_id=created.json()['id']
        forbidden=client.get(f'/api/playlists/{playlist_id}/videos',headers=viewer)
        assert forbidden.status_code == 403
        owner_view=client.get(f'/api/playlists/{playlist_id}/videos',headers=owner)
        assert owner_view.status_code == 200
