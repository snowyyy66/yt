import os

from redis import Redis

QUEUE = "video-processing"


def enqueue(video_id: str) -> None:
    connection = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), socket_connect_timeout=3)
    try:
        connection.rpush(QUEUE, video_id)
    finally:
        connection.close()
