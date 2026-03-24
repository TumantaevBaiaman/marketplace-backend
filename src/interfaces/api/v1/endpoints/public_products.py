import uuid

from fastapi import APIRouter, Depends, Query

from src.application.dto.product_dto import ProductDetailsDTO, ProductListResponseDTO
from src.application.queries.product_queries import (
    GetPublicProductDetailsQuery,
    ListPublicProductsQuery,
)
from src.application.services.product_service import ProductService
from src.interfaces.api.v1.dependencies import get_product_service

router = APIRouter(prefix="/public/products", tags=["Public"])


@router.get("/", response_model=ProductListResponseDTO)
async def list_products(
    limit: int = Query(default=20, ge=1, le=100),
    cursor: str | None = Query(default=None),
    in_stock: bool = Query(default=False),
    sort: str = Query(default="default", enum=["default", "price_asc", "price_desc", "rating"]),
    service: ProductService = Depends(get_product_service),
) -> ProductListResponseDTO:
    return await service.list_public(
        ListPublicProductsQuery(
            limit=limit,
            cursor=cursor,
            in_stock=in_stock,
            sort=sort,
        )
    )


@router.get("/{product_id}", response_model=ProductDetailsDTO)
async def get_product(
    product_id: uuid.UUID,
    offers_sort: str = Query(default="price", enum=["price", "delivery_date"]),
    service: ProductService = Depends(get_product_service),
) -> ProductDetailsDTO:
    return await service.get_public_details(
        GetPublicProductDetailsQuery(
            product_id=product_id,
            offers_sort=offers_sort,
        )
    )
