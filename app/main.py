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
