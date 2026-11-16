from datetime import timedelta
from functools import lru_cache
import os

from minio import Minio


@lru_cache

def client(public: bool = False) -> Minio:
    configured = os.getenv("S3_PUBLIC_ENDPOINT") if public else None
    endpoint = configured or os.getenv("S3_ENDPOINT", "localhost:9000")
    endpoint = endpoint.removeprefix("http://").removeprefix("https://")
    secure = (configured or os.getenv("S3_ENDPOINT", "http://localhost:9000")).startswith("https://")
    return Minio(endpoint, access_key=os.getenv("MINIO_ROOT_USER", "yt-local"), secret_key=os.getenv("MINIO_ROOT_PASSWORD", "change-this-minio-password"), secure=secure)


def bucket_name() -> str:
    return os.getenv("S3_BUCKET", "videos")


def ensure_bucket() -> None:
    storage = client()
    bucket = bucket_name()
    if not storage.bucket_exists(bucket):
        storage.make_bucket(bucket)


def signed_url(object_key: str) -> str:
    ensure_bucket()
    return client(public=True).presigned_get_object(bucket_name(), object_key, expires=timedelta(minutes=5))
