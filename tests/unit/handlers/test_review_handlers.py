import pytest
import uuid
from unittest.mock import AsyncMock

from src.application.handlers.command_handlers.review_command_handlers import CreateReviewHandler
from src.application.commands.review_commands import CreateReviewCommand
from src.application.dto.review_dto import ReviewResponseDTO
from src.domain.exceptions.domain_exceptions import BusinessRuleViolation
from tests.conftest import make_review


class TestCreateReviewHandler:
    @pytest.mark.asyncio
    async def test_creates_review_and_returns_dto(self, mock_review_repo):
        mock_review_repo.get_by_user_and_product = AsyncMock(return_value=None)

        product_id = uuid.uuid4()
        user_id = uuid.uuid4()

        handler = CreateReviewHandler(mock_review_repo)
        result = await handler.handle(CreateReviewCommand(
            product_id=product_id,
            user_id=user_id,
            author="John Doe",
            rating=5,
            text="Excellent product!",
        ))

        mock_review_repo.save.assert_called_once()
        assert isinstance(result, ReviewResponseDTO)
        assert result.rating == 5
        assert result.author == "John Doe"
        assert result.text == "Excellent product!"
        assert result.product_id == product_id
        assert result.user_id == user_id

    @pytest.mark.asyncio
    async def test_raises_when_user_already_reviewed(self, mock_review_repo):
        product_id = uuid.uuid4()
        user_id = uuid.uuid4()
        existing = make_review(product_id=product_id, user_id=user_id)
        mock_review_repo.get_by_user_and_product = AsyncMock(return_value=existing)

        handler = CreateReviewHandler(mock_review_repo)
        with pytest.raises(BusinessRuleViolation):
            await handler.handle(CreateReviewCommand(
                product_id=product_id,
                user_id=user_id,
                author="John Doe",
                rating=4,
                text="Another review",
            ))

    @pytest.mark.asyncio
    async def test_does_not_save_on_duplicate(self, mock_review_repo):
        existing = make_review()
        mock_review_repo.get_by_user_and_product = AsyncMock(return_value=existing)

        handler = CreateReviewHandler(mock_review_repo)
        with pytest.raises(BusinessRuleViolation):
            await handler.handle(CreateReviewCommand(
                product_id=existing.product_id,
                user_id=existing.user_id,
                author="John",
                rating=1,
                text="Bad",
            ))

        mock_review_repo.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_different_users_can_review_same_product(self, mock_review_repo):
        product_id = uuid.uuid4()
        mock_review_repo.get_by_user_and_product = AsyncMock(return_value=None)

        handler = CreateReviewHandler(mock_review_repo)

        for i in range(3):
            await handler.handle(CreateReviewCommand(
                product_id=product_id,
                user_id=uuid.uuid4(),
                author=f"User {i}",
                rating=5,
                text="Great!",
            ))

        assert mock_review_repo.save.call_count == 3

    @pytest.mark.asyncio
    async def test_review_dto_contains_id(self, mock_review_repo):
        mock_review_repo.get_by_user_and_product = AsyncMock(return_value=None)

        handler = CreateReviewHandler(mock_review_repo)
        result = await handler.handle(CreateReviewCommand(
            product_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            author="Jane",
            rating=3,
            text="Average",
        ))

        assert result.id is not None
