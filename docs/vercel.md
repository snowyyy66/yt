# Развёртывание всего приложения на Vercel

Vercel запускает FastAPI как одну Python Function. Этот же FastAPI обслуживает HTML-интерфейс и API, а файлы под `/static/` Vercel раздаёт через CDN. Отдельный адрес API и прокси на `api.example.com` не нужны. Такой способ официально поддерживается Vercel для FastAPI и `StaticFiles`.

## Подключение проекта

1. В Vercel открой существующий проект `yt`, подключённый к `snowyyy66/yt`.
2. В настройках проекта оставь Framework Preset `FastAPI`, если Vercel его распознал. Не задавай собственные Build Command и Output Directory.
3. В Storage проекта добавь PostgreSQL из Marketplace. Для медиа создай bucket в Cloudflare R2 (или другом S3-совместимом managed-сервисе); запускать свой сервер не требуется. Приложение использует MinIO SDK, поэтому Vercel Blob нельзя подставить вместо S3 без адаптера. Vercel не запускает PostgreSQL или Silo из Docker Compose.
4. В Environment Variables проекта добавь production значения:

   - `DATABASE_URL` — строка подключения к PostgreSQL, доступная из Vercel.
   - `APP_SECRET` — длинный случайный секрет.
   - `S3_ENDPOINT` и `S3_PUBLIC_ENDPOINT` — HTTPS endpoints S3; для этого деплоя они могут совпадать.
   - `S3_BUCKET`, `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`, `S3_REGION` — имя bucket и его credentials. Для Cloudflare R2 укажи `S3_REGION=auto` и используй S3 API endpoint аккаунта `https://<account-id>.r2.cloudflarestorage.com`.
   - `VIDEO_WORKER_ENABLED=false` — для демо без фонового worker.

5. Сохрани переменные и сделай Redeploy. Адрес сайта выдаёт Vercel, покупать домен не обязательно.

6. В настройках R2 bucket добавь CORS policy: разреши `PUT`, `GET`, `HEAD` с origin адреса деплоя (`https://<project>.vercel.app`) и локального адреса разработки. Разрешённый заголовок — `Content-Type`; expose headers не требуются. Если у проекта появится preview-домен, добавь и его точный origin. `S3_PUBLIC_ENDPOINT` должен быть браузерно-доступным HTTPS S3 endpoint bucket, чтобы подписанный URL открывался с сайта.

## Что будет работать

Регистрация, вход, API, комментарии, лайки, приватный доступ, каналы и модерация работают в одном Vercel-проекте после подключения PostgreSQL и S3. Видео в этой демо-конфигурации сразу доступно для просмотра в исходном формате, но FFmpeg-обработка и создание превью не запускаются, потому что постоянный worker не является частью Vercel Function.

Vercel Functions ограничивают размер тела запроса 4,5 МБ, поэтому файл не проходит через FastAPI. FastAPI создаёт запись и выдаёт подписанный на 15 минут URL для прямой загрузки в R2. После передачи сервер сверяет размер и сигнатуру файла и только затем делает его доступным. В приложении действует лимит 2 ГБ; на Vercel реальный лимит также зависит от ограничений тарифа и настроек object storage. Worker с FFmpeg доступен в Docker deployment, а на Vercel его выключают через `VIDEO_WORKER_ENABLED=false`.

## Логи

Логи FastAPI смотри в Vercel: открой проект → **Logs**. Логи frontend/API будут в одном проекте. Для диагностики базы и object storage смотри журналы соответствующих managed-сервисов.

Локальный Docker Compose остаётся для разработки и полного тестирования worker с FFmpeg.
