# Database design

PostgreSQL stores normalized application metadata. Planned entities are `users`, `videos`, `video_access_grants`, `comments`, `video_likes`, `channels`, `subscriptions`, `playlists`, `playlist_items`, and `reports`.

Users own videos and channels. A video stores visibility, moderation state, processing state, and object keys. A grant links one private video to one permitted user. Comments, likes, reports, and playlist entries reference their owning records with foreign keys. Unique constraints will prevent duplicate likes, subscriptions, and grants.

The schema will be introduced through versioned migrations as each API slice is implemented. Video and thumbnail bytes remain in S3-compatible object storage.
