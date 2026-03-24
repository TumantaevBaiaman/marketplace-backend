import uuid

from fastapi import APIRouter, Depends

from src.application.commands.offer_commands import (
    CreateOfferCommand,
    DeleteOfferCommand,
    UpdateOfferCommand,
)
from src.application.dto.offer_dto import (
    AdminOfferCreateDTO,
    AdminOfferResponseDTO,
    AdminOfferUpdateDTO,
)
from src.application.queries.offer_queries import GetOffersByProductQuery
from src.application.services.offer_service import OfferService
from src.interfaces.api.v1.dependencies import get_current_admin, get_offer_service

router = APIRouter(tags=["AdminOffers"])


@router.get("/admin/products/{product_id}/offers", response_model=list[AdminOfferResponseDTO])
async def list_offers(
    product_id: uuid.UUID,
    _=Depends(get_current_admin),
    service: OfferService = Depends(get_offer_service),
):
    return await service.get_by_product(GetOffersByProductQuery(product_id=product_id))


@router.post(
    "/admin/products/{product_id}/offers", response_model=AdminOfferResponseDTO, status_code=201
)
async def create_offer(
    product_id: uuid.UUID,
    dto: AdminOfferCreateDTO,
    _=Depends(get_current_admin),
    service: OfferService = Depends(get_offer_service),
):
    return await service.create(
        CreateOfferCommand(
            product_id=product_id,
            seller_id=dto.seller_id,
            price_amount=dto.price.amount,
            price_currency=dto.price.currency,
            delivery_date=dto.delivery_date,
            condition=dto.condition,
            quantity=dto.quantity,
            is_available=dto.is_available,
            delivery_days_min=dto.delivery_days_min,
            delivery_days_max=dto.delivery_days_max,
        )
    )


@router.put("/admin/offers/{offer_id}", response_model=AdminOfferResponseDTO)
async def update_offer(
    offer_id: uuid.UUID,
    dto: AdminOfferUpdateDTO,
    _=Depends(get_current_admin),
    service: OfferService = Depends(get_offer_service),
):
    return await service.update(
        UpdateOfferCommand(
            offer_id=offer_id,
            seller_id=dto.seller_id,
            price_amount=dto.price.amount if dto.price else None,
            price_currency=dto.price.currency if dto.price else None,
            delivery_date=dto.delivery_date,
            condition=dto.condition,
            quantity=dto.quantity,
            is_available=dto.is_available,
            delivery_days_min=dto.delivery_days_min,
            delivery_days_max=dto.delivery_days_max,
        )
    )


@router.delete("/admin/offers/{offer_id}", status_code=204)
async def delete_offer(
    offer_id: uuid.UUID,
    _=Depends(get_current_admin),
    service: OfferService = Depends(get_offer_service),
):
    await service.delete(DeleteOfferCommand(offer_id=offer_id))
