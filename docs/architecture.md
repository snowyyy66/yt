# Architecture

The first deployment uses Docker Compose. FastAPI owns the HTTP boundary and OpenAPI contract. PostgreSQL is the source of truth for accounts, video metadata, grants, and interactions. MinIO stores original and processed media objects; the database stores object keys, never media bytes. Redis is reserved for job coordination and caching.

Video delivery will use short-lived signed object URLs after API authorization. Private video grants are checked before a URL is issued. Uploads will be size-limited, stored under server-generated keys, and processed asynchronously before becoming playable.

The initial API skeleton does not claim database or object-store readiness; `/health` confirms only that the HTTP process responds. Feature work adds dependency-aware readiness and migrations.
