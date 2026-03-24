from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import get_settings

_settings = get_settings()

engine = create_async_engine(
    _settings.db.url,
    echo=_settings.db.echo,
    pool_size=_settings.db.pool_size,
    max_overflow=_settings.db.max_overflow,
    pool_timeout=_settings.db.pool_timeout,
)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    await engine.dispose()


async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
