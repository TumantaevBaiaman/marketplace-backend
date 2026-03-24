import redis.asyncio as redis

from src.config import get_settings

_settings = get_settings()

redis_client: redis.Redis | None = None


async def get_redis() -> redis.Redis:
    return redis_client


async def init_redis() -> None:
    global redis_client
    redis_client = await redis.from_url(_settings.redis.url, decode_responses=True)


async def close_redis() -> None:
    if redis_client:
        await redis_client.aclose()
