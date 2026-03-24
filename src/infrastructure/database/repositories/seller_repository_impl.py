import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.seller import Seller
from src.domain.repositories.seller_repository import SellerRepository
from src.infrastructure.database.models.seller_model import SellerModel


class SQLAlchemySellerRepository(SellerRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, seller_id: uuid.UUID) -> Seller | None:
        model = await self._session.get(SellerModel, seller_id)
        return self._to_entity(model) if model else None

    async def get_all(self) -> list[Seller]:
        result = await self._session.execute(select(SellerModel).order_by(SellerModel.id))
        return [self._to_entity(m) for m in result.scalars().all()]

    async def save(self, seller: Seller) -> Seller:
        model = await self._session.get(SellerModel, seller.id)
        if model:
            model.name = seller.name
            model.description = seller.description
            model.email = seller.email
            model.phone = seller.phone
            model.website = seller.website
            model.country = seller.country
            model.rating = seller.rating
            model.review_count = seller.review_count
            model.is_verified = seller.is_verified
        else:
            model = SellerModel(
                id=seller.id,
                name=seller.name,
                description=seller.description,
                email=seller.email,
                phone=seller.phone,
                website=seller.website,
                country=seller.country,
                rating=seller.rating,
                review_count=seller.review_count,
                is_verified=seller.is_verified,
            )
            self._session.add(model)
        await self._session.commit()
        return seller

    def _to_entity(self, model: SellerModel) -> Seller:
        return Seller(
            id=model.id,
            name=model.name,
            description=model.description,
            email=model.email,
            phone=model.phone,
            website=model.website,
            country=model.country,
            rating=model.rating,
            review_count=model.review_count or 0,
            is_verified=model.is_verified or False,
        )
