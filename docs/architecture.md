# Architecture

Docker Compose runs the FastAPI application, PostgreSQL, MinIO, and Redis. FastAPI owns the HTTP and OpenAPI boundary. PostgreSQL is the source of truth for accounts, comments, likes, videos, private access grants, subscriptions, and reports. MinIO stores video bytes; the database stores object keys and access policy.

Uploads require a bearer token, accept video MIME types up to 2 GiB, and use server-generated object keys. Playback checks visibility before issuing a five-minute signed URL. The public MinIO endpoint is configurable separately from the internal endpoint so a browser can reach the object URL.

Passwords are hashed with scrypt. API tokens are signed HMAC tokens with a 24-hour expiry. Roles are `user`, `moderator`, and `admin`; moderation endpoints require one of the latter roles. The demo feed is static and the API stores newly uploaded media records in PostgreSQL.

Redis queues uploaded video IDs. A separate worker uses FFmpeg to normalize each file to MP4, generates a thumbnail, stores both objects in MinIO, and changes the video state from `processing` to `ready`. Failed jobs are marked `failed`. Adaptive HLS/DASH output is not implemented.
