from src.application.commands.review_commands import CreateReviewCommand
from src.application.dto.review_dto import ReviewResponseDTO
from src.domain.entities.review import Review
from src.domain.exceptions.domain_exceptions import BusinessRuleViolation
from src.domain.repositories.review_repository import ReviewRepository


def _to_dto(review: Review) -> ReviewResponseDTO:
    return ReviewResponseDTO(
        id=review.id,
        product_id=review.product_id,
        user_id=review.user_id,
        author=review.author,
        rating=review.rating,
        text=review.text,
        created_at=review.created_at,
    )


class CreateReviewHandler:
    def __init__(self, review_repo: ReviewRepository):
        self._reviews = review_repo

    async def handle(self, command: CreateReviewCommand) -> ReviewResponseDTO:
        existing = await self._reviews.get_by_user_and_product(command.user_id, command.product_id)
        if existing:
            raise BusinessRuleViolation("Вы уже оставили отзыв на этот товар")

        review = Review(
            product_id=command.product_id,
            user_id=command.user_id,
            author=command.author,
            rating=command.rating,
            text=command.text,
        )
        await self._reviews.save(review)
        return _to_dto(review)
