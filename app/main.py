from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Видосфера", description="Пародийный видеохостинг", version="0.1.0")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

VIDEOS = [
    {"id": "v1", "title": "Как я нажал «пропустить рекламу» 47 раз", "channel": "Кот Борисыч", "views": "2,4 млн просмотров", "age": "2 дня назад", "color": "coral", "duration": "12:48", "category": "Для вас"},
    {"id": "v2", "title": "Собрал компьютер из того, что нашёл под диваном", "channel": "Паяльник и печеньки", "views": "840 тыс. просмотров", "age": "5 часов назад", "color": "blue", "duration": "28:03", "category": "Технологии"},
    {"id": "v3", "title": "Рецепт идеального бутерброда. Спонсор: хлеб", "channel": "Шеф на районе", "views": "1,1 млн просмотров", "age": "1 неделю назад", "color": "yellow", "duration": "08:17", "category": "Кулинария"},
    {"id": "v4", "title": "Поставил будильник на 6:00. Проснулся в 11:32", "channel": "Планировщик жизни", "views": "320 тыс. просмотров", "age": "Вчера", "color": "green", "duration": "16:41", "category": "Для вас"},
    {"id": "v5", "title": "Топ-10 причин посмотреть это видео до конца", "channel": "Алгоритм рекомендует", "views": "9,8 млн просмотров", "age": "3 недели назад", "color": "purple", "duration": "10:00", "category": "Популярное"},
    {"id": "v6", "title": "Распаковываю коробку, в которой была другая коробка", "channel": "Почта России unboxing", "views": "75 тыс. просмотров", "age": "4 дня назад", "color": "orange", "duration": "21:09", "category": "Развлечения"},
    {"id": "v7", "title": "Белый шум: сосед сверлит стену (8 часов)", "channel": "Звуки панельки", "views": "4,2 млн просмотров", "age": "1 месяц назад", "color": "slate", "duration": "8:00:00", "category": "Музыка"},
    {"id": "v8", "title": "Обзор обзора на обзор нового телефона", "channel": "Обзорщик обзоров", "views": "612 тыс. просмотров", "age": "6 дней назад", "color": "pink", "duration": "19:52", "category": "Технологии"},
]


@app.get("/health", tags=["operations"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "yt"}


@app.get("/api/videos", tags=["videos"])
def list_videos() -> list[dict[str, str]]:
    return VIDEOS


@app.get("/api/videos/{video_id}", tags=["videos"])
def get_video(video_id: str):
    return next((video for video in VIDEOS if video["id"] == video_id), {"detail": "Видео не найдено"})


@app.get("/{page}", include_in_schema=False)
def frontend_page(page: str):
    return FileResponse("app/static/index.html")


@app.get("/", include_in_schema=False)
def homepage():
    return FileResponse("app/static/index.html")
from fastapi import Depends, Header, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Comment, Like, SessionLocal, User
from app.security import hash_password, issue_token, read_token, verify_password


def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def current_user(authorization: str | None = Header(default=None), session: Session = Depends(db_session)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Войди, чтобы продолжить")
    user_id = read_token(authorization[7:])
    user = session.get(User, user_id) if user_id else None
    if user is None:
        raise HTTPException(status_code=401, detail="Сессия закончилась, войди ещё раз")
    return user


class RegisterInput(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=1, max_length=80)


class LoginInput(BaseModel):
    email: EmailStr
    password: str


class CommentInput(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


@app.post("/api/auth/register", status_code=201, tags=["accounts"])
def register(data: RegisterInput, session: Session = Depends(db_session)):
    user = User(email=data.email.lower(), password_hash=hash_password(data.password), name=data.name.strip())
    session.add(user)
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=409, detail="Этот адрес уже зарегистрирован") from error
    return {"access_token": issue_token(user.id), "token_type": "bearer"}


@app.post("/api/auth/login", tags=["accounts"])
def login(data: LoginInput, session: Session = Depends(db_session)):
    user = session.scalar(select(User).where(User.email == data.email.lower()))
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверная почта или пароль")
    return {"access_token": issue_token(user.id), "token_type": "bearer"}


@app.get("/api/auth/me", tags=["accounts"])
def me(user: User = Depends(current_user)):
    return {"id": user.id, "email": user.email, "name": user.name, "role": user.role}


@app.get("/api/videos/{video_id}/comments", tags=["videos"])
def get_comments(video_id: str, session: Session = Depends(db_session)):
    rows = session.scalars(select(Comment).where(Comment.video_id == video_id).order_by(Comment.created_at.desc()).limit(100)).all()
    return [{"id": row.id, "text": row.text, "author": session.get(User, row.user_id).name} for row in rows]


@app.post("/api/videos/{video_id}/comments", status_code=201, tags=["videos"])
def add_comment(video_id: str, data: CommentInput, user: User = Depends(current_user), session: Session = Depends(db_session)):
    if not any(video["id"] == video_id for video in VIDEOS):
        raise HTTPException(status_code=404, detail="Видео не найдено")
    comment = Comment(video_id=video_id, user_id=user.id, text=data.text.strip())
    session.add(comment)
    session.commit()
    return {"id": comment.id, "text": comment.text, "author": user.name}


@app.put("/api/videos/{video_id}/like", tags=["videos"])
def toggle_like(video_id: str, user: User = Depends(current_user), session: Session = Depends(db_session)):
    if not any(video["id"] == video_id for video in VIDEOS):
        raise HTTPException(status_code=404, detail="Видео не найдено")
    like = session.scalar(select(Like).where(Like.video_id == video_id, Like.user_id == user.id))
    if like is None:
        like = Like(video_id=video_id, user_id=user.id, active=True)
        session.add(like)
    else:
        like.active = not like.active
    session.commit()
    count = session.scalar(select(Like).where(Like.video_id == video_id, Like.active.is_(True)).count()) if False else None
    return {"liked": like.active}
from uuid import uuid4

from fastapi import File, Form, UploadFile
from sqlalchemy import func

from app.media_models import Report, Subscription, VideoGrant, VideoRecord

class AccessInput(BaseModel):
    email: EmailStr


class ReportInput(BaseModel):
    reason: str = Field(min_length=3, max_length=500)


@app.post("/api/videos", status_code=201, tags=["videos"])
def upload_video(file: UploadFile = File(...), title: str = Form(min_length=1, max_length=100), description: str = Form(default=""), visibility: str = Form(default="public"), user: User = Depends(current_user), session: Session = Depends(db_session)):
    if visibility not in {"public", "private"}:
        raise HTTPException(status_code=422, detail="Выбери открытый или приватный доступ")
    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(status_code=415, detail="Нужен файл видеоформата")
    if file.size is None or file.size == 0 or file.size > 2 * 1024 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Размер видео должен быть от 1 байта до 2 ГБ")
    from app import storage

    video_id = uuid4().hex
    key = f"original/{video_id}"
    try:
        storage.ensure_bucket()
        storage.client().put_object(storage.bucket_name(), key, file.file, file.size, content_type=file.content_type)
    except Exception as error:
        raise HTTPException(status_code=503, detail="Хранилище видео временно недоступно") from error
    video = VideoRecord(id=video_id, owner_id=user.id, title=title.strip(), description=description, object_key=key, visibility=visibility, status="ready")
    session.add(video)
    session.commit()
    return {"id": video.id, "title": video.title, "visibility": video.visibility, "status": video.status}


@app.get("/api/videos/{video_id}/play", tags=["videos"])
def play_video(video_id: str, authorization: str | None = Header(default=None), session: Session = Depends(db_session)):
    from app import storage

    video = session.get(VideoRecord, video_id)
    if video is None or video.hidden:
        raise HTTPException(status_code=404, detail="Видео не найдено")
    if video.visibility == "private":
        user_id = read_token(authorization[7:]) if authorization and authorization.startswith("Bearer ") else None
        if user_id is None:
            raise HTTPException(status_code=401, detail="Войди, чтобы посмотреть приватное видео")
        if user_id != video.owner_id and session.scalar(select(VideoGrant).where(VideoGrant.video_id == video_id, VideoGrant.user_id == user_id)) is None:
            raise HTTPException(status_code=403, detail="Владелец пока не поделился этим видео")
    return {"url": storage.signed_url(video.object_key), "expires_in": 300}


@app.post("/api/videos/{video_id}/access", status_code=201, tags=["videos"])
def grant_video_access(video_id: str, data: AccessInput, user: User = Depends(current_user), session: Session = Depends(db_session)):
    video = session.get(VideoRecord, video_id)
    if video is None:
        raise HTTPException(status_code=404, detail="Видео не найдено")
    if video.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Разрешать доступ может только владелец")
    target = session.scalar(select(User).where(User.email == data.email.lower()))
    if target is None:
        raise HTTPException(status_code=404, detail="Сначала попроси пользователя зарегистрироваться")
    exists = session.scalar(select(VideoGrant).where(VideoGrant.video_id == video_id, VideoGrant.user_id == target.id))
    if exists is None:
        session.add(VideoGrant(video_id=video_id, user_id=target.id))
        session.commit()
    return {"granted": True, "email": target.email}


@app.put("/api/channels/{channel_id}/subscribe", tags=["channels"])
def subscribe(channel_id: int, user: User = Depends(current_user), session: Session = Depends(db_session)):
    if session.get(User, channel_id) is None:
        raise HTTPException(status_code=404, detail="Канал не найден")
    if channel_id == user.id:
        raise HTTPException(status_code=400, detail="Нельзя подписаться на собственный канал")
    record = session.scalar(select(Subscription).where(Subscription.subscriber_id == user.id, Subscription.channel_id == channel_id))
    if record is None:
        session.add(Subscription(subscriber_id=user.id, channel_id=channel_id))
        session.commit()
        return {"subscribed": True}
    session.delete(record)
    session.commit()
    return {"subscribed": False}


@app.get("/api/channels/{channel_id}/videos", tags=["channels"])
def channel_videos(channel_id: int, session: Session = Depends(db_session)):
    owner = session.get(User, channel_id)
    if owner is None:
        raise HTTPException(status_code=404, detail="Канал не найден")
    videos = session.scalars(select(VideoRecord).where(VideoRecord.owner_id == channel_id, VideoRecord.visibility == "public", VideoRecord.hidden.is_(False)).order_by(VideoRecord.created_at.desc())).all()
    return {"channel": {"id": owner.id, "name": owner.name}, "videos": [{"id": row.id, "title": row.title, "description": row.description} for row in videos]}


@app.post("/api/videos/{video_id}/reports", status_code=201, tags=["moderation"])
def report_video(video_id: str, data: ReportInput, user: User = Depends(current_user), session: Session = Depends(db_session)):
    if session.get(VideoRecord, video_id) is None and not any(video["id"] == video_id for video in VIDEOS):
        raise HTTPException(status_code=404, detail="Видео не найдено")
    report = Report(video_id=video_id, reporter_id=user.id, reason=data.reason)
    session.add(report)
    session.commit()
    return {"id": report.id, "status": report.status}


def require_moderator(user: User = Depends(current_user)) -> User:
    if user.role not in {"moderator", "admin"}:
        raise HTTPException(status_code=403, detail="Доступ только для модераторов")
    return user


@app.get("/api/moderation/reports", tags=["moderation"])
def moderation_reports(_: User = Depends(require_moderator), session: Session = Depends(db_session)):
    rows = session.scalars(select(Report).where(Report.status == "open").order_by(Report.created_at)).all()
    return [{"id": row.id, "video_id": row.video_id, "reason": row.reason, "status": row.status} for row in rows]


@app.post("/api/moderation/videos/{video_id}/hide", tags=["moderation"])
def hide_video(video_id: str, user: User = Depends(require_moderator), session: Session = Depends(db_session)):
    video = session.get(VideoRecord, video_id)
    if video is None:
        raise HTTPException(status_code=404, detail="Видео не найдено")
    video.hidden = True
    session.query(Report).filter(Report.video_id == video_id).update({"status": "reviewed"})
    session.commit()
    return {"video_id": video_id, "hidden": True, "moderated_by": user.id}

from app.models import Base, engine
Base.metadata.create_all(engine)
