from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.category import Category
from src.domain.repositories.category_repository import CategoryRepository
from src.infrastructure.database.models.category_model import CategoryModel


class SQLAlchemyCategoryRepository(CategoryRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_all(self) -> list[Category]:
        result = await self._session.execute(select(CategoryModel).order_by(CategoryModel.name))
        rows = result.scalars().all()
        return [self._to_entity(row) for row in rows]

    def _to_entity(self, model: CategoryModel) -> Category:
        return Category(
            id=model.id,
            name=model.name,
            slug=model.slug,
            description=model.description,
            icon_url=model.icon_url,
            parent_id=model.parent_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
