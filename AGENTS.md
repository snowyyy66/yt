# Project instructions

## Product direction

This is a Russian-language parody of a familiar video platform. Keep the recognizable video feed, player, channel, search, upload, account, playlist, and moderation flows. Keep the parody in the product name and copy; do not reuse YouTube logos or media. Seed-feed titles and counters are fictional and must remain labeled as demo content.

## Architecture

- FastAPI serves the API, OpenAPI docs, and static interface.
- PostgreSQL stores accounts and application metadata.
- Silo (S3-compatible with MinIO) stores original, normalized, and thumbnail objects.
- Redis queues uploads for the FFmpeg worker.
- Private media access is authorized before issuing a short-lived signed URL.

## Development rules

- Add a focused test before changing behavior and run it before implementation.
- Keep files and tests focused on one behavior.
- Never commit `.env`, generated media, or local databases.
- Use `python -m pytest -q` for the full test suite.
- Use `bash deploy.sh` on Ubuntu to install Docker if needed and start the stack.
- Keep user-facing interface text in Russian and retain labels, keyboard access, and mobile layout.

## Known boundaries

- SQLAlchemy creates tables at startup; versioned database migrations are not yet configured.
- The worker produces a normalized MP4 and a thumbnail, but adaptive HLS/DASH output is not implemented.
- Static parody cards without a seeded or uploaded media object show an explicit demo placeholder.
