import uuid
from abc import ABC, abstractmethod

from src.domain.entities.user_identity import UserIdentity
from src.domain.enums.auth_provider import AuthProvider


class UserIdentityRepository(ABC):
    @abstractmethod
    async def get_by_id(self, identity_id: uuid.UUID) -> UserIdentity | None: ...

    @abstractmethod
    async def get_by_provider(
        self, provider: AuthProvider, provider_id: str
    ) -> UserIdentity | None: ...

    @abstractmethod
    async def get_all_by_user(self, user_id: uuid.UUID) -> list[UserIdentity]: ...

    @abstractmethod
    async def save(self, identity: UserIdentity) -> UserIdentity: ...

    @abstractmethod
    async def delete(self, identity_id: uuid.UUID) -> None: ...
