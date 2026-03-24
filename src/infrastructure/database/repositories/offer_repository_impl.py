import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.offer import Offer
from src.domain.repositories.offer_repository import OfferRepository
from src.infrastructure.database.filters import apply_filters
from src.infrastructure.database.models.offer_model import OfferModel


class SQLAlchemyOfferRepository(OfferRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, offer_id: uuid.UUID) -> Offer | None:
        model = await self._session.get(OfferModel, offer_id)
        return self._to_entity(model) if model else None

    async def get_by_product(self, product_id: uuid.UUID, sort_by: str = "price") -> list[Offer]:
        order = OfferModel.price_amount if sort_by == "price" else OfferModel.delivery_date
        q = select(OfferModel).order_by(order)
        q = apply_filters(q, OfferModel, {"product_id": product_id})
        result = await self._session.execute(q)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def save(self, offer: Offer) -> Offer:
        model = await self._session.get(OfferModel, offer.id)
        if model:
            model.seller_id = offer.seller_id
            model.price_amount = offer.price_amount
            model.price_currency = offer.price_currency
            model.delivery_date = offer.delivery_date
            model.condition = offer.condition
            model.quantity = offer.quantity
            model.is_available = offer.is_available
            model.delivery_days_min = offer.delivery_days_min
            model.delivery_days_max = offer.delivery_days_max
        else:
            model = OfferModel(
                id=offer.id,
                product_id=offer.product_id,
                seller_id=offer.seller_id,
                price_amount=offer.price_amount,
                price_currency=offer.price_currency,
                delivery_date=offer.delivery_date,
                condition=offer.condition,
                quantity=offer.quantity,
                is_available=offer.is_available,
                delivery_days_min=offer.delivery_days_min,
                delivery_days_max=offer.delivery_days_max,
            )
            self._session.add(model)
        await self._session.commit()
        return offer

    async def delete(self, offer_id: uuid.UUID) -> None:
        model = await self._session.get(OfferModel, offer_id)
        if model:
            await self._session.delete(model)
            await self._session.commit()

    def _to_entity(self, model: OfferModel) -> Offer:
        return Offer(
            id=model.id,
            product_id=model.product_id,
            seller_id=model.seller_id,
            price_amount=model.price_amount,
            price_currency=model.price_currency.value
            if hasattr(model.price_currency, "value")
            else model.price_currency,
            delivery_date=model.delivery_date,
            condition=model.condition.value
            if hasattr(model.condition, "value")
            else model.condition,
            quantity=model.quantity,
            is_available=model.is_available,
            delivery_days_min=model.delivery_days_min,
            delivery_days_max=model.delivery_days_max,
        )
