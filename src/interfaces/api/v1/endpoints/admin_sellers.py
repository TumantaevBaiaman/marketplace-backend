import uuid

from fastapi import APIRouter, Depends

from src.application.commands.seller_commands import CreateSellerCommand, UpdateSellerCommand
from src.application.dto.seller_dto import (
    AdminSellerCreateDTO,
    AdminSellerResponseDTO,
    AdminSellerUpdateDTO,
)
from src.application.queries.seller_queries import ListSellersQuery
from src.application.services.seller_service import SellerService
from src.interfaces.api.v1.dependencies import get_current_admin, get_seller_service

router = APIRouter(prefix="/admin/sellers", tags=["AdminSellers"])


@router.get("/", response_model=list[AdminSellerResponseDTO])
async def list_sellers(
    _=Depends(get_current_admin),
    service: SellerService = Depends(get_seller_service),
):
    return await service.get_all(ListSellersQuery())


@router.post("/", response_model=AdminSellerResponseDTO, status_code=201)
async def create_seller(
    dto: AdminSellerCreateDTO,
    _=Depends(get_current_admin),
    service: SellerService = Depends(get_seller_service),
):
    return await service.create(
        CreateSellerCommand(
            name=dto.name,
            description=dto.description,
            email=dto.email,
            phone=dto.phone,
            website=dto.website,
            country=dto.country,
            rating=dto.rating,
            is_verified=dto.is_verified,
        )
    )


@router.put("/{seller_id}", response_model=AdminSellerResponseDTO)
async def update_seller(
    seller_id: uuid.UUID,
    dto: AdminSellerUpdateDTO,
    _=Depends(get_current_admin),
    service: SellerService = Depends(get_seller_service),
):
    return await service.update(
        UpdateSellerCommand(
            seller_id=seller_id,
            name=dto.name,
            description=dto.description,
            email=dto.email,
            phone=dto.phone,
            website=dto.website,
            country=dto.country,
            rating=dto.rating,
            is_verified=dto.is_verified,
        )
    )
