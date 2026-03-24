import uuid
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.entities.product import Product
from src.domain.repositories.product_repository import ProductRepository
from src.infrastructure.database.filters import apply_filters
from src.infrastructure.database.models.category_model import CategoryModel
from src.infrastructure.database.models.product_model import ProductModel
from src.infrastructure.database.models.review_model import ReviewModel
from src.infrastructure.database.pagination import cursor_paginate


class SQLAlchemyProductRepository(ProductRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, product_id: uuid.UUID) -> Product | None:
        result = await self._session.execute(
            select(ProductModel)
            .options(selectinload(ProductModel.attributes))
            .where(ProductModel.id == product_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_list(
        self,
        limit: int,
        cursor: uuid.UUID | None,
        in_stock: bool = False,
        sort: str = "default",
        search: str | None = None,
        is_active: bool | None = None,
        price_min: float | None = None,
        price_max: float | None = None,
    ) -> tuple[list[Product], uuid.UUID | None]:
        from src.infrastructure.database.models.review_model import ReviewModel as RM

        avg_rating_sub = (
            select(func.avg(RM.rating))
            .where(RM.product_id == ProductModel.id)
            .correlate(ProductModel)
            .scalar_subquery()
        )

        if sort == "rating":
            order = avg_rating_sub.desc()
        elif sort == "newest":
            order = ProductModel.created_at.desc()
        else:
            order = ProductModel.id.asc()

        q = select(ProductModel).order_by(order)
        q = apply_filters(
            q,
            ProductModel,
            {
                "stock__gt": 0 if in_stock else None,
                "is_active": is_active,
                "name__search": {"fields": [ProductModel.name, ProductModel.sku], "q": search}
                if search
                else None,
                "price_amount__gte": price_min,
                "price_amount__lte": price_max,
            },
        )

        page = await cursor_paginate(
            self._session,
            q,
            limit,
            cursor_value=cursor if sort == "default" else None,
            cursor_field=ProductModel.id,
        )
        return [self._to_entity(r) for r in page.items], page.next_cursor

    async def save(self, product: Product) -> Product:
        model = await self._session.get(ProductModel, product.id)
        if model:
            model.name = product.name
            model.description = product.description
            model.sku = product.sku
            model.category_id = product.category_id
            model.price_amount = product.price_amount
            model.price_currency = product.price_currency
            model.stock = product.stock
            model.is_active = product.is_active
            model.image_object_key = product.image_object_key
            model.thumbnail_object_key = product.thumbnail_object_key
        else:
            model = ProductModel(
                id=product.id,
                name=product.name,
                description=product.description,
                sku=product.sku,
                category_id=product.category_id,
                price_amount=product.price_amount,
                price_currency=product.price_currency,
                stock=product.stock,
                is_active=product.is_active,
                image_object_key=product.image_object_key,
                thumbnail_object_key=product.thumbnail_object_key,
            )
            self._session.add(model)
        try:
            await self._session.commit()
            await self._session.refresh(model)
        except IntegrityError as e:
            await self._session.rollback()
            if "uq_products_sku" in str(e) or "sku" in str(e):
                raise ValueError("Товар с таким артикулом (SKU) уже существует")
            raise
        return product

    async def delete(self, product_id: uuid.UUID) -> None:
        model = await self._session.get(ProductModel, product_id)
        if model:
            await self._session.delete(model)
            await self._session.commit()

    async def count(self) -> int:
        result = await self._session.execute(select(func.count()).select_from(ProductModel))
        return result.scalar() or 0

    async def get_ratings(
        self, product_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, tuple[float | None, int]]:
        if not product_ids:
            return {}
        result = await self._session.execute(
            select(
                ReviewModel.product_id,
                func.avg(ReviewModel.rating).label("avg_rating"),
                func.count(ReviewModel.id).label("review_count"),
            )
            .where(ReviewModel.product_id.in_(product_ids))
            .group_by(ReviewModel.product_id)
        )
        return {
            row.product_id: (round(float(row.avg_rating), 2), row.review_count) for row in result
        }

    async def get_category_name(self, category_id: uuid.UUID) -> str | None:
        result = await self._session.execute(
            select(CategoryModel.name).where(CategoryModel.id == category_id)
        )
        return result.scalar_one_or_none()

    def _to_entity(self, model: ProductModel) -> Product:
        return Product(
            id=model.id,
            name=model.name,
            description=getattr(model, "description", None),
            sku=getattr(model, "sku", None),
            category_id=getattr(model, "category_id", None),
            price_amount=getattr(model, "price_amount", Decimal("0")),
            price_currency=model.price_currency.value
            if hasattr(model.price_currency, "value")
            else model.price_currency,
            stock=getattr(model, "stock", 0),
            is_active=getattr(model, "is_active", True) or True,
            image_object_key=model.image_object_key,
            thumbnail_object_key=model.thumbnail_object_key,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
