# Architecture

Docker Compose runs the FastAPI application, PostgreSQL, Silo (an S3-compatible MinIO fork), and Redis. FastAPI owns the HTTP and OpenAPI boundary. PostgreSQL is the source of truth for accounts, comments, likes, videos, private access grants, subscriptions, and reports. Silo stores video bytes; the database stores object keys and access policy.

Uploads require a bearer token, accept video MIME types up to 2 GiB, and use server-generated object keys. The API issues a short-lived signed PUT URL so the browser sends file bytes directly to S3-compatible storage rather than through the FastAPI request body. The completion endpoint verifies object size and video signature before making the record playable. Playback checks visibility before issuing a five-minute signed URL. The public S3 endpoint is configurable separately from the internal endpoint so a browser can reach the object URL.

Passwords are hashed with scrypt. API tokens are signed HMAC tokens with a 24-hour expiry. Roles are `user`, `moderator`, and `admin`; moderation endpoints require one of the latter roles. The demo feed is static and the API stores newly uploaded media records in PostgreSQL.

Redis queues uploaded video IDs. A separate worker uses FFmpeg to normalize each file to MP4, generates a thumbnail, stores both objects in Silo, and changes the video state from `processing` to `ready`. Failed jobs are marked `failed`. Adaptive HLS/DASH output is not implemented.
