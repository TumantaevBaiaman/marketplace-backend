"""
Скрипт создания администратора.

Запуск:
    docker exec marketplace-stack-backend-1 python3 -m src.infrastructure.database.create_admin

Переменные окружения (опционально, иначе используются значения по умолчанию):
    ADMIN_EMAIL      — email администратора     (default: admin@marketplace.com)
    ADMIN_PASSWORD   — пароль администратора    (default: Admin1234!)
    ADMIN_FIRST_NAME — имя                      (default: Admin)
    ADMIN_LAST_NAME  — фамилия                  (default: User)
"""

import asyncio
import os
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import src.infrastructure.database.models  # noqa: F401 — registers all ORM mappers
from src.config import get_settings
from src.domain.enums.auth_provider import AuthProvider
from src.domain.enums.user_role import UserRole
from src.domain.enums.user_status import UserStatus
from src.infrastructure.database.models.user_identity_model import UserIdentityModel
from src.infrastructure.database.models.user_model import UserModel
from src.infrastructure.logging import configure_logging, get_logger
from src.infrastructure.security.password import hash_password

configure_logging()
logger = get_logger(__name__)
settings = get_settings()

EMAIL = os.getenv("ADMIN_EMAIL", "admin@marketplace.com")
PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin1234!")
FIRST_NAME = os.getenv("ADMIN_FIRST_NAME", "Admin")
LAST_NAME = os.getenv("ADMIN_LAST_NAME", "User")


async def create_admin(session: AsyncSession) -> None:
    # Проверяем — вдруг уже существует
    existing = await session.execute(
        select(UserIdentityModel).where(
            UserIdentityModel.provider == AuthProvider.EMAIL,
            UserIdentityModel.provider_id == EMAIL,
        )
    )
    if existing.scalar_one_or_none():
        logger.warning("Администратор с email '%s' уже существует. Пропускаем.", EMAIL)
        return

    user_id = uuid.uuid4()

    user = UserModel(
        id=user_id,
        first_name=FIRST_NAME,
        last_name=LAST_NAME,
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
    )
    session.add(user)
    await session.flush()

    identity = UserIdentityModel(
        id=uuid.uuid4(),
        user_id=user_id,
        provider=AuthProvider.EMAIL,
        provider_id=EMAIL,
        credential_hash=hash_password(PASSWORD),
        is_verified=True,
    )
    session.add(identity)
    await session.commit()

    logger.info("✓ Администратор создан")
    logger.info("  Email:    %s", EMAIL)
    logger.info("  Password: %s", PASSWORD)
    logger.info("  Role:     %s", UserRole.ADMIN)


async def main() -> None:
    engine = create_async_engine(settings.db.url, echo=False)
    maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with maker() as session:
        await create_admin(session)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
