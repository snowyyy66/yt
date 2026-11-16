# Развёртывание всего приложения на Vercel

Vercel запускает FastAPI как одну Python Function. Этот же FastAPI обслуживает HTML-интерфейс и API, а файлы под `/static/` Vercel раздаёт через CDN. Отдельный адрес API и прокси на `api.example.com` не нужны. Такой способ официально поддерживается Vercel для FastAPI и `StaticFiles`.

## Подключение проекта

1. В Vercel открой существующий проект `yt`, подключённый к `snowyyy66/yt`.
2. В настройках проекта оставь Framework Preset `FastAPI`, если Vercel его распознал. Не задавай собственные Build Command и Output Directory.
3. В Storage проекта добавь PostgreSQL из Marketplace. Файловое хранилище код сейчас ожидает как S3-совместимый managed-сервис; запускать свой сервер не требуется. Vercel Blob нельзя подставить вместо S3 без адаптера, потому что приложение использует MinIO SDK. Vercel не запускает PostgreSQL или Silo из Docker Compose.
4. В Environment Variables проекта добавь production значения:

   - `DATABASE_URL` — строка подключения к PostgreSQL, доступная из Vercel.
   - `APP_SECRET` — длинный случайный секрет.
   - `S3_ENDPOINT` и `S3_PUBLIC_ENDPOINT` — HTTPS endpoints S3; для этого деплоя они могут совпадать.
   - `S3_BUCKET`, `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`, `S3_REGION` — имя bucket и его credentials.
   - `VIDEO_WORKER_ENABLED=false` — для демо без фонового worker.

5. Сохрани переменные и сделай Redeploy. Адрес сайта выдаёт Vercel, покупать домен не обязательно.

## Что будет работать

Регистрация, вход, API, комментарии, лайки, приватный доступ, каналы и модерация работают в одном Vercel-проекте после подключения PostgreSQL и S3. Видео в этой демо-конфигурации сразу доступно для просмотра в исходном формате, но FFmpeg-обработка и создание превью не запускаются, потому что постоянный worker не является частью Vercel Function.

Vercel Functions ограничивают размер тела запроса 4,5 МБ. Поэтому текущая загрузка видео через FastAPI подходит только для небольших демонстрационных клипов. Для больших файлов нужна отдельная доработка прямой загрузки из браузера в object storage. [Vercel описывает клиентскую загрузку в Blob как способ обхода этого лимита](https://vercel.com/docs/vercel-blob/client-upload), но её нужно интегрировать в приложение и учесть приватные видео.

## Логи

Логи FastAPI смотри в Vercel: открой проект → **Logs**. Логи frontend/API будут в одном проекте. Для диагностики базы и object storage смотри журналы соответствующих managed-сервисов.

Локальный Docker Compose остаётся для разработки и полного тестирования worker с FFmpeg.
