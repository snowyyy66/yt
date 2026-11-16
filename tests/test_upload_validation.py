from fastapi.testclient import TestClient
from app.main import app


def test_upload_rejects_video_mime_with_non_video_contents():
    with TestClient(app) as client:
        email=f"{__import__('uuid').uuid4().hex}@example.com"
        result=client.post('/api/auth/register',json={'email':email,'password':'long-password-123','name':'Автор'}).json()
        headers={'Authorization':f"Bearer {result['access_token']}"}
        response=client.post('/api/videos',headers=headers,data={'title':'Подделка'},files={'file':('fake.mp4',b'this-is-not-video','video/mp4')})
        assert response.status_code==415
