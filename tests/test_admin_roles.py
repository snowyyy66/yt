from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy import select
from app.main import app
from app.models import SessionLocal, User


def account(client, name, role='user'):
    email=f"{uuid4().hex}@example.com"
    result=client.post('/api/auth/register',json={'email':email,'password':'long-password-123','name':name})
    headers={'Authorization':f"Bearer {result.json()['access_token']}"}
    if role!='user':
        with SessionLocal() as session:
            user=session.scalar(select(User).where(User.email==email));user.role=role;session.commit()
    return headers,email


def test_admin_can_assign_a_moderator_role():
    with TestClient(app) as client:
        admin,_=account(client,'Админ','admin')
        target,email=account(client,'Будущий модератор')
        with SessionLocal() as session:
            member=session.scalar(select(User).where(User.email==email))
            user_id=member.id
        result=client.put(f'/api/admin/users/{user_id}/role',headers=admin,json={'role':'moderator'})
        assert result.status_code==200
        profile=client.get('/api/auth/me',headers=target)
        assert profile.json()['role']=='moderator'
