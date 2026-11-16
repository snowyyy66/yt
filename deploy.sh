#!/usr/bin/env bash
set -euo pipefail

if [ ! -f .env ]; then
  cp .env.example .env
  python3 - <<'PY'
from pathlib import Path
import secrets
path = Path('.env')
text = path.read_text()
text = text.replace('change-me', secrets.token_urlsafe(32))
text = text.replace('change-this-minio-password', secrets.token_urlsafe(32))
text = text.replace('replace-with-a-long-random-secret', secrets.token_urlsafe(48))
path.write_text(text)
PY
fi

docker compose up --build -d
printf '\nВидосфера запущена: http://localhost:8000\nДокументация API: http://localhost:8000/docs\n'
