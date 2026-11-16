from uuid import uuid4
from fastapi.testclient import TestClient
from app.main import app


def test_signed_in_comment_is_saved_and_returned_by_video_endpoint():
    email=f"{uuid4().hex}@example.com"
    with TestClient(app) as client:
        login=client.post('/api/auth/register',json={'email':email,'password':'long-password-123','name':'Комментатор'}).json()
        headers={'Authorization':f"Bearer {login['access_token']}"}
        created=client.post('/api/videos/v1/comments',headers=headers,json={'text':'Сохрани этот комментарий'})
        assert created.status_code==201
        comments=client.get('/api/videos/v1/comments').json()
        assert any(item['text']=='Сохрани этот комментарий' for item in comments)


def test_like_requires_authentication_and_is_toggleable():
    email=f"{uuid4().hex}@example.com"
    with TestClient(app) as client:
        assert client.put('/api/videos/v1/like').status_code==401
        login=client.post('/api/auth/register',json={'email':email,'password':'long-password-123','name':'Зритель'}).json()
        headers={'Authorization':f"Bearer {login['access_token']}"}
        assert client.put('/api/videos/v1/like',headers=headers).json()['liked'] is True
        assert client.put('/api/videos/v1/like',headers=headers).json()['liked'] is False


def test_like_response_contains_persisted_active_count():
    email=f"{uuid4().hex}@example.com"
    with TestClient(app) as client:
        login=client.post('/api/auth/register',json={'email':email,'password':'long-password-123','name':'Зритель'}).json()
        headers={'Authorization':f"Bearer {login['access_token']}"}

        liked=client.put('/api/videos/v1/like',headers=headers)
        assert liked.json()['liked'] is True
        assert liked.json()['count'] >= 1

        unliked=client.put('/api/videos/v1/like',headers=headers)
        assert unliked.json()['liked'] is False
        assert unliked.json()['count'] == liked.json()['count'] - 1


def test_like_state_is_available_before_toggling():
    email=f"{uuid4().hex}@example.com"
    with TestClient(app) as client:
        login=client.post('/api/auth/register',json={'email':email,'password':'long-password-123','name':'Зритель'}).json()
        headers={'Authorization':f"Bearer {login['access_token']}"}
        initial=client.get('/api/videos/v1/like',headers=headers)
        assert initial.status_code == 200
        assert initial.json()['liked'] is False
        assert initial.json()['count'] >= 0

        client.put('/api/videos/v1/like',headers=headers)
        current=client.get('/api/videos/v1/like',headers=headers)
        assert current.json()['liked'] is True
