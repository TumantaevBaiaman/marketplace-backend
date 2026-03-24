from src.domain.services.token_service import ITokenService
from src.infrastructure.cache.token_blacklist import blacklist_token
from src.infrastructure.security.jwt_service import create_access_token


class TokenServiceImpl(ITokenService):
    def __init__(self, redis_client):
        self._redis = redis_client

    def create_access_token(self, data: dict) -> str:
        return create_access_token(data)

    async def blacklist_token(self, jti: str, ttl_seconds: int) -> None:
        await blacklist_token(self._redis, jti, ttl_seconds)
