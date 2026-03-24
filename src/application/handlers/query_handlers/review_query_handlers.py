from src.application.dto.review_dto import ReviewListDTO, ReviewResponseDTO
from src.application.queries.review_queries import GetMyReviewQuery, ListReviewsQuery
from src.domain.entities.review import Review
from src.domain.repositories.review_repository import ReviewRepository


def _to_dto(r: Review) -> ReviewResponseDTO:
    return ReviewResponseDTO(
        id=r.id,
        product_id=r.product_id,
        user_id=r.user_id,
        author=r.author,
        rating=r.rating,
        text=r.text,
        created_at=r.created_at,
    )


class ListReviewsHandler:
    def __init__(self, review_repo: ReviewRepository):
        self._reviews = review_repo

    async def handle(self, query: ListReviewsQuery) -> ReviewListDTO:
        items = await self._reviews.get_by_product(query.product_id)
        avg = round(sum(r.rating for r in items) / len(items), 2) if items else None
        return ReviewListDTO(
            items=[_to_dto(r) for r in items],
            total=len(items),
            avg_rating=avg,
        )


class GetMyReviewHandler:
    def __init__(self, review_repo: ReviewRepository):
        self._reviews = review_repo

    async def handle(self, query: GetMyReviewQuery) -> ReviewResponseDTO | None:
        review = await self._reviews.get_by_user_and_product(query.user_id, query.product_id)
        return _to_dto(review) if review else None
