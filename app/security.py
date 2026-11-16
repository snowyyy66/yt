import base64
import hashlib
import hmac
import json
import os
import secrets
import time

SECRET = os.getenv("APP_SECRET", "local-development-secret-change-this")


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return f"{salt.hex()}:{digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, digest_hex = stored.split(":", 1)
        digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt_hex), n=2**14, r=8, p=1)
        return hmac.compare_digest(digest.hex(), digest_hex)
    except (ValueError, TypeError):
        return False


def issue_token(user_id: int) -> str:
    header = _encode({"alg": "HS256", "typ": "JWT"})
    payload = _encode({"sub": str(user_id), "exp": int(time.time()) + 86400})
    signature = _sign(f"{header}.{payload}")
    return f"{header}.{payload}.{signature}"


def read_token(token: str) -> int | None:
    try:
        header, payload, signature = token.split(".")
        if not hmac.compare_digest(signature, _sign(f"{header}.{payload}")):
            return None
        values = json.loads(_decode(payload))
        if values["exp"] < time.time():
            return None
        return int(values["sub"])
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        return None


def _encode(value: dict) -> str:
    return base64.urlsafe_b64encode(json.dumps(value, separators=(",", ":")).encode()).decode().rstrip("=")


def _decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _sign(value: str) -> str:
    digest = hmac.new(SECRET.encode(), value.encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).decode().rstrip("=")
