import asyncio
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import pool
from alembic import context
from src.config import get_settings
from src.infrastructure.database.base import Base

# import models so alembic can detect them
import src.infrastructure.database.models.user_model  # noqa: F401
import src.infrastructure.database.models.user_identity_model  # noqa: F401
import src.infrastructure.database.models.product_model  # noqa: F401
import src.infrastructure.database.models.product_attribute_model  # noqa: F401
import src.infrastructure.database.models.seller_model  # noqa: F401
import src.infrastructure.database.models.offer_model  # noqa: F401
import src.infrastructure.database.models.review_model  # noqa: F401
import src.infrastructure.database.models.product_audit_log_model  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = str(get_settings().db.url)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    # Используем URL-объект напрямую — избегаем проблем с экранированием спецсимволов в пароле
    connectable = create_async_engine(
        get_settings().db.url,
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
