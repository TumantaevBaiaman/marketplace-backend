from src.application.dto.category_dto import CategoryDTO
from src.application.handlers.query_handlers.category_query_handlers import GetCategoriesHandler
from src.application.queries.category_queries import GetCategoriesQuery
from src.domain.repositories.category_repository import CategoryRepository


class CategoryService:
    def __init__(self, category_repo: CategoryRepository):
        self._get_categories_handler = GetCategoriesHandler(category_repo)

    async def get_categories(self, query: GetCategoriesQuery) -> list[CategoryDTO]:
        return await self._get_categories_handler.handle(query)
