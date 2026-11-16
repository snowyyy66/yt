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
