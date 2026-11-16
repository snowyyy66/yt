# YouTube-like Video Platform Implementation Plan

> **For agentic workers:** Use this plan task-by-task. Keep each behavior test-first and commit each coherent change.

**Goal:** Build a deployable video sharing application with account roles, private access, uploads, playback, interactions, search, channels, and moderation.

**Architecture:** FastAPI serves the API and static frontend, PostgreSQL stores users and metadata, MinIO stores media objects, and Redis with a worker handles media processing. The first vertical slice establishes the service skeleton and health checks; features follow as independently testable increments.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy, PostgreSQL, MinIO (S3), Redis, pytest, HTML/CSS/JavaScript frontend, Docker Compose.

**Spec:** User-provided YouTube copy test assignment in the conversation.

## Global Constraints

- Python + FastAPI and PostgreSQL are fixed requirements.
- Swagger must be available at `/docs`.
- A clean Ubuntu host must be deployable with one command.
- Media bytes belong in object storage; PostgreSQL holds metadata and access policy.
- Roles are user, moderator, administrator; private video access is owner-controlled.
- Commits use the repository owner's Git identity and preserve incremental history.

## Review Focus

- Missing database or object store: health endpoint reports readiness accurately.
- Uploads with unsafe names or excessive size: reject before persistence.
- Private media requested by an unauthorized account: deny access.
- Duplicate likes/subscriptions: remain idempotent.
- Unauthenticated moderation actions: reject.

## Tasks

### Task 1: Repository foundation

**Files:** `pyproject.toml`, `Dockerfile`, `docker-compose.yml`, `.env.example`, `.gitignore`, `README.md`, `docs/architecture.md`, `docs/database.md`, `prompts/README.md`, `app/main.py`, `tests/test_health.py`.

- [ ] Add app health test and observe failure.
- [ ] Implement FastAPI health endpoint and OpenAPI metadata.
- [ ] Configure Postgres, MinIO, Redis and app services for one-command deployment.
- [ ] Document architecture, data ownership, setup, and prompt/session artifact policy.
- [ ] Run the test suite and commit the foundation.

### Task 2: Accounts and authorization

- [ ] Test registration, login, password hashing, token identity, and role restrictions.
- [ ] Implement user schema and auth endpoints.
- [ ] Commit the account slice.

### Task 3: Video metadata and private access

- [ ] Test video ownership, visibility grants, and forbidden private access.
- [ ] Implement video and access grant schema/endpoints.
- [ ] Commit the metadata slice.

### Task 4: Object storage and upload lifecycle

- [ ] Test upload policy, multipart lifecycle, object isolation, and status transitions.
- [ ] Implement signed upload/download and worker processing.
- [ ] Commit media pipeline.

### Task 5: Discovery and interactions

- [ ] Test search, likes, comments, channel listing, playlists, and subscriptions.
- [ ] Implement endpoints and frontend views.
- [ ] Commit API and UI slices.

### Task 6: Moderation and delivery

- [ ] Test reporting, moderator actions, and admin role handling.
- [ ] Implement moderation and seed data.
- [ ] Add clean-host deployment and end-to-end documentation.
- [ ] Run verification and commit release-ready state.
