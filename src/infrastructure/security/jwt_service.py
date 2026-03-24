import uuid
from datetime import datetime, timedelta, timezone

import jwt

from src.config import get_settings

_settings = get_settings()


def create_access_token(payload: dict) -> str:
    data = payload.copy()
    data["jti"] = str(uuid.uuid4())
    data["exp"] = datetime.now(timezone.utc) + timedelta(
        minutes=_settings.jwt.access_token_expire_minutes
    )
    data["type"] = "access"
    return jwt.encode(data, _settings.jwt.secret_key, algorithm=_settings.jwt.algorithm)


def create_refresh_token(payload: dict) -> str:
    data = payload.copy()
    data["jti"] = str(uuid.uuid4())
    data["exp"] = datetime.now(timezone.utc) + timedelta(
        days=_settings.jwt.refresh_token_expire_days
    )
    data["type"] = "refresh"
    return jwt.encode(data, _settings.jwt.secret_key, algorithm=_settings.jwt.algorithm)


def decode_token(token: str) -> dict:
    return jwt.decode(token, _settings.jwt.secret_key, algorithms=[_settings.jwt.algorithm])
