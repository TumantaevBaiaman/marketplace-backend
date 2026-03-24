from src.application.dto.category_dto import CategoryDTO
from src.application.queries.category_queries import GetCategoriesQuery
from src.domain.entities.category import Category
from src.domain.repositories.category_repository import CategoryRepository


def _to_dto(category: Category) -> CategoryDTO:
    return CategoryDTO(
        id=category.id,
        name=category.name,
        slug=category.slug,
        parent_id=category.parent_id,
    )


class GetCategoriesHandler:
    def __init__(self, category_repo: CategoryRepository):
        self._categories = category_repo

    async def handle(self, query: GetCategoriesQuery) -> list[CategoryDTO]:
        categories = await self._categories.get_all()
        return [_to_dto(c) for c in categories]
