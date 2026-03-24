import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.product_attribute import ProductAttribute
from src.domain.repositories.product_attribute_repository import ProductAttributeRepository
from src.infrastructure.database.filters import apply_filters
from src.infrastructure.database.models.product_attribute_model import ProductAttributeModel


class SQLAlchemyProductAttributeRepository(ProductAttributeRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_product(self, product_id: uuid.UUID) -> list[ProductAttribute]:
        q = select(ProductAttributeModel)
        q = apply_filters(q, ProductAttributeModel, {"product_id": product_id})
        result = await self._session.execute(q)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def save(self, attr: ProductAttribute) -> ProductAttribute:
        model = ProductAttributeModel(
            id=attr.id,
            product_id=attr.product_id,
            key=attr.key,
            value=attr.value,
        )
        self._session.add(model)
        await self._session.commit()
        return attr

    async def delete_by_product(self, product_id: uuid.UUID) -> None:
        await self._session.execute(
            delete(ProductAttributeModel).where(ProductAttributeModel.product_id == product_id)
        )
        await self._session.commit()

    def _to_entity(self, model: ProductAttributeModel) -> ProductAttribute:
        return ProductAttribute(
            id=model.id, product_id=model.product_id, key=model.key, value=model.value
        )
