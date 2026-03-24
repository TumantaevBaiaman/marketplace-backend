from src.application.commands.review_commands import CreateReviewCommand
from src.application.handlers.command_handlers.review_command_handlers import CreateReviewHandler
from src.application.handlers.query_handlers.review_query_handlers import (
    GetMyReviewHandler,
    ListReviewsHandler,
)
from src.application.queries.review_queries import GetMyReviewQuery, ListReviewsQuery
from src.domain.repositories.review_repository import ReviewRepository


class ReviewService:
    def __init__(self, review_repo: ReviewRepository):
        self._create_handler = CreateReviewHandler(review_repo)
        self._list_handler = ListReviewsHandler(review_repo)
        self._my_review_handler = GetMyReviewHandler(review_repo)

    async def create(self, command: CreateReviewCommand):
        return await self._create_handler.handle(command)

    async def list_reviews(self, query: ListReviewsQuery):
        return await self._list_handler.handle(query)

    async def get_my_review(self, query: GetMyReviewQuery):
        return await self._my_review_handler.handle(query)
