import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user_identity import UserIdentity
from src.domain.enums.auth_provider import AuthProvider
from src.domain.repositories.user_identity_repository import UserIdentityRepository
from src.infrastructure.database.filters import apply_filters
from src.infrastructure.database.models.user_identity_model import UserIdentityModel


class SQLAlchemyUserIdentityRepository(UserIdentityRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, identity_id: uuid.UUID) -> UserIdentity | None:
        model = await self._session.get(UserIdentityModel, identity_id)
        return self._to_entity(model) if model else None

    async def get_by_provider(
        self, provider: AuthProvider, provider_id: str
    ) -> UserIdentity | None:
        result = await self._session.execute(
            select(UserIdentityModel).where(
                UserIdentityModel.provider == provider,
                UserIdentityModel.provider_id == provider_id,
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_all_by_user(self, user_id: uuid.UUID) -> list[UserIdentity]:
        q = select(UserIdentityModel)
        q = apply_filters(q, UserIdentityModel, {"user_id": user_id})
        result = await self._session.execute(q)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def save(self, identity: UserIdentity) -> UserIdentity:
        model = await self._session.get(UserIdentityModel, identity.id)
        if model:
            model.credential_hash = identity.credential_hash
            model.is_verified = identity.is_verified
        else:
            model = UserIdentityModel(
                id=identity.id,
                user_id=identity.user_id,
                provider=identity.provider,
                provider_id=identity.provider_id,
                credential_hash=identity.credential_hash,
                is_verified=identity.is_verified,
                created_at=identity.created_at,
            )
            self._session.add(model)
        await self._session.commit()
        return identity

    async def delete(self, identity_id: uuid.UUID) -> None:
        model = await self._session.get(UserIdentityModel, identity_id)
        if model:
            await self._session.delete(model)
            await self._session.commit()

    def _to_entity(self, model: UserIdentityModel) -> UserIdentity:
        return UserIdentity(
            id=model.id,
            user_id=model.user_id,
            provider=AuthProvider(model.provider),
            provider_id=model.provider_id,
            credential_hash=model.credential_hash,
            is_verified=model.is_verified,
            created_at=model.created_at,
        )
