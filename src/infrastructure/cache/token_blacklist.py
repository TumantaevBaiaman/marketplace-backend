import redis.asyncio as redis

_BLACKLIST_PREFIX = "blacklist:jti:"


async def blacklist_token(redis_client: redis.Redis, jti: str, ttl_seconds: int) -> None:
    """Добавить jti в blacklist на время жизни токена."""
    await redis_client.setex(f"{_BLACKLIST_PREFIX}{jti}", ttl_seconds, "1")


async def is_token_blacklisted(redis_client: redis.Redis, jti: str) -> bool:
    """Проверить, находится ли jti в blacklist."""
    return await redis_client.exists(f"{_BLACKLIST_PREFIX}{jti}") == 1
