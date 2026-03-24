import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.review import Review
from src.domain.repositories.review_repository import ReviewRepository
from src.infrastructure.database.filters import apply_filters
from src.infrastructure.database.models.review_model import ReviewModel


class SQLAlchemyReviewRepository(ReviewRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_product(self, product_id: uuid.UUID) -> list[Review]:
        q = select(ReviewModel).order_by(ReviewModel.created_at.desc())
        q = apply_filters(q, ReviewModel, {"product_id": product_id})
        result = await self._session.execute(q)
        return [self._to_entity(r) for r in result.scalars().all()]

    async def get_by_user_and_product(
        self, user_id: uuid.UUID, product_id: uuid.UUID
    ) -> Review | None:
        result = await self._session.execute(
            select(ReviewModel).where(
                ReviewModel.user_id == user_id,
                ReviewModel.product_id == product_id,
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def save(self, review: Review) -> Review:
        model = await self._session.get(ReviewModel, review.id)
        if model:
            model.rating = review.rating
            model.text = review.text
            model.author = review.author
        else:
            model = ReviewModel(
                id=review.id,
                product_id=review.product_id,
                user_id=review.user_id,
                author=review.author,
                rating=review.rating,
                text=review.text,
                is_verified_purchase=review.is_verified_purchase,
                helpful_count=review.helpful_count,
            )
            self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return review

    def _to_entity(self, model: ReviewModel) -> Review:
        return Review(
            id=model.id,
            product_id=model.product_id,
            user_id=model.user_id,
            author=model.author,
            rating=model.rating,
            text=model.text,
            is_verified_purchase=model.is_verified_purchase,
            helpful_count=model.helpful_count,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
