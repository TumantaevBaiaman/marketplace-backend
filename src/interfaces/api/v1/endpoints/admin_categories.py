from fastapi import APIRouter, Depends

from src.application.dto.category_dto import CategoryDTO
from src.application.queries.category_queries import GetCategoriesQuery
from src.application.services.category_service import CategoryService
from src.interfaces.api.v1.dependencies import get_category_service, get_current_admin

router = APIRouter(prefix="/admin/categories", tags=["AdminCategories"])


@router.get("/", response_model=list[CategoryDTO])
async def list_categories(
    _=Depends(get_current_admin),
    service: CategoryService = Depends(get_category_service),
) -> list[CategoryDTO]:
    return await service.get_categories(GetCategoriesQuery())
