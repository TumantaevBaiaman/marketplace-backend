"""
Удаляет все тестовые данные (товары, продавцы, офферы, отзывы).
Run: docker exec marketplace-stack-backend-1 python3 -m src.infrastructure.database.seed_clear
"""

import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import get_settings
from src.infrastructure.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)
settings = get_settings()

TABLES = ["reviews", "offers", "product_attributes", "products", "sellers"]


async def clear() -> None:
    engine = create_async_engine(settings.db.url, echo=False)
    maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with maker() as session:
        for table in TABLES:
            await session.execute(text(f"TRUNCATE {table} RESTART IDENTITY CASCADE"))
        await session.commit()
        logger.info("All data cleared: %s", ", ".join(TABLES))
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(clear())
