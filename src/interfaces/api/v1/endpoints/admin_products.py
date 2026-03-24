import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from src.application.commands.product_commands import (
    CreateProductCommand,
    DeleteProductCommand,
    UpdateProductCommand,
    UploadProductImageCommand,
)
from src.application.dto.audit_dto import AuditLogListDTO
from src.application.dto.product_dto import (
    AdminProductCreateDTO,
    AdminProductResponseDTO,
    AdminProductUpdateDTO,
)
from src.application.queries.audit_queries import GetProductAuditLogQuery
from src.application.queries.product_queries import AdminGetProductQuery, AdminListProductsQuery
from src.application.services.product_service import ProductService
from src.interfaces.api.v1.dependencies import get_current_admin, get_product_service

router = APIRouter(prefix="/admin/products", tags=["AdminProducts"])


def _actor(admin: dict) -> tuple[uuid.UUID | None, str | None]:
    """Extract actor_id and actor_email from JWT payload."""
    raw_id = admin.get("sub")
    actor_id = uuid.UUID(raw_id) if raw_id else None
    actor_email = admin.get("email")
    return actor_id, actor_email


@router.get("/count")
async def count_products(
    _=Depends(get_current_admin),
    service: ProductService = Depends(get_product_service),
):
    return {"count": await service.admin_count()}


@router.get("/")
async def list_products(
    limit: int = 50,
    cursor: str | None = None,
    sort: str = "default",
    search: str | None = None,
    is_active: bool | None = None,
    in_stock: bool = False,
    price_min: float | None = None,
    price_max: float | None = None,
    _=Depends(get_current_admin),
    service: ProductService = Depends(get_product_service),
):
    return await service.admin_list(
        AdminListProductsQuery(
            limit=limit,
            cursor=cursor,
            sort=sort,
            search=search,
            is_active=is_active,
            in_stock=in_stock,
            price_min=price_min,
            price_max=price_max,
        )
    )


@router.post("/", response_model=AdminProductResponseDTO, status_code=201)
async def create_product(
    dto: AdminProductCreateDTO,
    admin=Depends(get_current_admin),
    service: ProductService = Depends(get_product_service),
):
    actor_id, actor_email = _actor(admin)
    try:
        return await service.admin_create(
            CreateProductCommand(
                name=dto.name,
                price_amount=dto.price.amount,
                price_currency=dto.price.currency,
                stock=dto.stock,
                description=dto.description,
                sku=dto.sku,
                category_id=dto.category_id,
                attributes=[{"key": a.key, "value": a.value} for a in dto.attributes],
                actor_id=actor_id,
                actor_email=actor_email,
            )
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{product_id}", response_model=AdminProductResponseDTO)
async def get_product(
    product_id: uuid.UUID,
    _=Depends(get_current_admin),
    service: ProductService = Depends(get_product_service),
):
    return await service.admin_get(AdminGetProductQuery(product_id=product_id))


@router.put("/{product_id}", response_model=AdminProductResponseDTO)
async def update_product(
    product_id: uuid.UUID,
    dto: AdminProductUpdateDTO,
    admin=Depends(get_current_admin),
    service: ProductService = Depends(get_product_service),
):
    actor_id, actor_email = _actor(admin)
    attrs = (
        [{"key": a.key, "value": a.value} for a in dto.attributes]
        if dto.attributes is not None
        else None
    )
    try:
        return await service.admin_update(
            UpdateProductCommand(
                product_id=product_id,
                name=dto.name,
                description=dto.description,
                sku=dto.sku,
                category_id=dto.category_id,
                price_amount=dto.price.amount if dto.price else None,
                price_currency=dto.price.currency if dto.price else None,
                stock=dto.stock,
                is_active=dto.is_active,
                attributes=attrs,
                actor_id=actor_id,
                actor_email=actor_email,
            )
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: uuid.UUID,
    admin=Depends(get_current_admin),
    service: ProductService = Depends(get_product_service),
):
    actor_id, actor_email = _actor(admin)
    await service.admin_delete(
        DeleteProductCommand(
            product_id=product_id,
            actor_id=actor_id,
            actor_email=actor_email,
        )
    )


@router.post("/{product_id}/image")
async def upload_image(
    product_id: uuid.UUID,
    file: UploadFile = File(...),
    _=Depends(get_current_admin),
    service: ProductService = Depends(get_product_service),
):
    data = await file.read()
    return await service.admin_upload_image(
        UploadProductImageCommand(
            product_id=product_id,
            data=data,
            content_type=file.content_type,
        )
    )


@router.get("/{product_id}/audit-log", response_model=AuditLogListDTO)
async def get_audit_log(
    product_id: uuid.UUID,
    limit: int = 50,
    _=Depends(get_current_admin),
    service: ProductService = Depends(get_product_service),
):
    result = await service.get_audit_log(
        GetProductAuditLogQuery(product_id=product_id, limit=limit)
    )
    if result is None:
        return AuditLogListDTO(entries=[])
    return result
