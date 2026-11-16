# YT

A self-hosted video sharing service built with FastAPI, PostgreSQL, MinIO, and Redis.

## Run locally

Copy `.env.example` to `.env`, change the development passwords, then run:

```sh
docker compose up --build -d
```

Open the API docs at <http://localhost:8000/docs>. MinIO console is at <http://localhost:9001>.

## Architecture

See [docs/architecture.md](docs/architecture.md) and [docs/database.md](docs/database.md). The API currently exposes `/health`; feature slices are tracked in [the implementation plan](docs/superpowers/plans/2026-11-17-video-platform.md).

## Tests

```sh
python -m pip install -e '.[test]'
python -m pytest
```

Do not use production secrets in `.env`; the example credentials are for local development only.
