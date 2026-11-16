#!/usr/bin/env bash
set -euo pipefail

if ! command -v docker >/dev/null 2>&1; then
  sudo apt-get update
  sudo apt-get install -y docker.io docker-compose-v2 python3
fi
if ! docker compose version >/dev/null 2>&1; then
  sudo apt-get update
  sudo apt-get install -y docker-compose-v2
fi
sudo systemctl enable --now docker

DOCKER=(docker)
if ! docker info >/dev/null 2>&1; then
  DOCKER=(sudo docker)
fi

if [ ! -f .env ]; then
  cp .env.example .env
fi
python3 - <<'PY'
from pathlib import Path
import secrets
path = Path('.env')
text = path.read_text()
text = text.replace('change-me', secrets.token_urlsafe(32))
text = text.replace('change-this-minio-password', secrets.token_urlsafe(32))
text = text.replace('replace-with-a-long-random-secret', secrets.token_urlsafe(48))
text = text.replace('replace-with-a-long-demo-password', secrets.token_urlsafe(24))
path.write_text(text)
PY

"${DOCKER[@]}" compose up --build -d
printf '\nВидосфера запущена: http://localhost:8000\nДокументация API: http://localhost:8000/docs\n'
