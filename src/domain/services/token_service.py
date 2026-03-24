from abc import ABC, abstractmethod


class ITokenService(ABC):
    @abstractmethod
    def create_access_token(self, data: dict) -> str: ...

    @abstractmethod
    async def blacklist_token(self, jti: str, ttl_seconds: int) -> None: ...
