from datetime import UTC, datetime, timedelta
import logging
from typing import Any

import bcrypt
import redis.asyncio as aioredis
from redis.exceptions import RedisError
from jose import JWTError, jwt

from core.config import settings

logger = logging.getLogger(__name__)

_redis: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _redis


# ── Password ─────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    password = plain.encode("utf-8")
    if len(password) > 72:
        raise ValueError("Password cannot be longer than 72 bytes.")
    return bcrypt.hashpw(password, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    password = plain.encode("utf-8")
    if len(password) > 72:
        return False
    return bcrypt.checkpw(password, hashed.encode("utf-8"))


# ── JWT ──────────────────────────────────────────────────────────────

def _create_token(data: dict[str, Any], expires_delta: timedelta) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(UTC) + expires_delta
    payload["iat"] = datetime.now(UTC)
    return jwt.encode(payload, settings.app_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(user_id: str, role: str) -> str:
    return _create_token(
        {"sub": user_id, "role": role, "type": "access"},
        timedelta(minutes=settings.access_token_expire_minutes),
    )


def create_refresh_token(user_id: str) -> str:
    return _create_token(
        {"sub": user_id, "type": "refresh"},
        timedelta(days=settings.refresh_token_expire_days),
    )


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.app_secret_key, algorithms=[settings.jwt_algorithm])


# ── Token Blacklist (Redis) ───────────────────────────────────────────

_BLACKLIST_PREFIX = "jwt_blacklist:"


async def blacklist_token(jti: str, ttl_seconds: int) -> None:
    try:
        r = await get_redis()
        await r.setex(f"{_BLACKLIST_PREFIX}{jti}", ttl_seconds, "1")
    except RedisError as exc:
        logger.debug("Redis unavailable; token blacklist write skipped: %s", exc)


async def is_token_blacklisted(jti: str) -> bool:
    try:
        r = await get_redis()
        return await r.exists(f"{_BLACKLIST_PREFIX}{jti}") == 1
    except RedisError as exc:
        logger.debug("Redis unavailable; token blacklist check skipped: %s", exc)
        return False


def verify_access_token(token: str) -> dict[str, Any]:
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise JWTError("Not an access token")
        return payload
    except JWTError as exc:
        raise ValueError(str(exc)) from exc
