import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user import User
from src.domain.enums.auth_provider import AuthProvider
from src.domain.enums.user_role import UserRole
from src.domain.enums.user_status import UserStatus
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.database.models.user_identity_model import UserIdentityModel
from src.infrastructure.database.models.user_model import UserModel


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        model = await self._session.get(UserModel, user_id)
        return self._to_entity(model) if model else None

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(
            select(UserModel)
            .join(UserIdentityModel, UserIdentityModel.user_id == UserModel.id)
            .where(
                UserIdentityModel.provider == AuthProvider.EMAIL,
                UserIdentityModel.provider_id == email,
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_all(self) -> list[User]:
        result = await self._session.execute(select(UserModel))
        return [self._to_entity(m) for m in result.scalars().all()]

    async def save(self, user: User) -> User:
        model = await self._session.get(UserModel, user.id)
        if model:
            model.role = user.role
            model.status = user.status
            model.first_name = user.first_name
            model.last_name = user.last_name
            model.avatar_url = user.avatar_url
            model.updated_at = user.updated_at
        else:
            model = UserModel(
                id=user.id,
                role=user.role,
                status=user.status,
                first_name=user.first_name,
                last_name=user.last_name,
                avatar_url=user.avatar_url,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
            self._session.add(model)
        await self._session.commit()
        return user

    async def delete(self, user_id: uuid.UUID) -> None:
        model = await self._session.get(UserModel, user_id)
        if model:
            await self._session.delete(model)
            await self._session.commit()

    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,
            role=UserRole(model.role),
            status=UserStatus(model.status),
            first_name=model.first_name,
            last_name=model.last_name,
            avatar_url=model.avatar_url,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
