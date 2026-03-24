import uuid

from src.application.dto.auth_dto import MeResponse
from src.application.dto.user_dto import UserResponseDTO
from src.application.queries.user_queries import (
    GetCurrentUserQuery,
    GetUserByEmailQuery,
    GetUserByIdQuery,
)
from src.domain.entities.user import User
from src.domain.enums.auth_provider import AuthProvider
from src.domain.repositories.user_identity_repository import UserIdentityRepository
from src.domain.repositories.user_repository import UserRepository


def _to_dto(user: User) -> UserResponseDTO:
    return UserResponseDTO(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        is_active=user.is_active,
        avatar_url=user.avatar_url,
    )


class GetUserByIdHandler:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    async def handle(self, query: GetUserByIdQuery) -> UserResponseDTO | None:
        user = await self._user_repo.get_by_id(uuid.UUID(query.user_id))
        return _to_dto(user) if user else None


class GetUserByEmailHandler:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    async def handle(self, query: GetUserByEmailQuery) -> UserResponseDTO | None:
        user = await self._user_repo.get_by_email(query.email)
        return _to_dto(user) if user else None


class GetCurrentUserHandler:
    def __init__(self, user_repo: UserRepository, identity_repo: UserIdentityRepository):
        self._user_repo = user_repo
        self._identity_repo = identity_repo

    async def handle(self, query: GetCurrentUserQuery) -> MeResponse | None:
        user = await self._user_repo.get_by_id(uuid.UUID(query.user_id))
        if not user:
            return None

        identities = await self._identity_repo.get_all_by_user(user.id)
        email_identity = next(
            (i for i in identities if i.provider == AuthProvider.EMAIL),
            None,
        )

        return MeResponse(
            id=user.id,
            email=email_identity.provider_id if email_identity else "",
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            is_admin=user.is_admin,
        )
