# Database schema

PostgreSQL is the source of truth for users, uploaded media metadata, grants, comments, likes, subscriptions, playlists, and reports. Media bytes live in MinIO under server-generated keys. The schema currently uses SQLAlchemy metadata creation at application startup; a versioned migration system is still needed before long-lived production operation.

## Relationships

- `users` owns videos and playlists, and acts as the target for channel subscriptions.
- `videos.owner_id` references `users.id`; `videos.object_key` references a MinIO object.
- `video_access_grants` links a private video to an allowed user with a unique pair constraint.
- `comments`, `video_likes`, and `reports` point to a video and its author/reporter. `video_likes` enforces one row per user/video pair.
- `subscriptions` prevents duplicate channel follows.
- `playlists` belongs to a user; `playlist_items` links videos to a playlist and enforces uniqueness.

The static parody feed entries are presentation fixtures. The demo seed script creates a database record and comments for one fixture, but no playable bytes for that fixture.
