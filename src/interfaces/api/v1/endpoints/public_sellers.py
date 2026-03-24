import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.application.services.seller_service import SellerService
from src.interfaces.api.v1.dependencies import get_seller_service


class PublicSellerDTO(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None = None
    email: str | None = None
    phone: str | None = None
    website: str | None = None
    country: str | None = None
    rating: Decimal
    review_count: int = 0
    is_verified: bool = False


router = APIRouter(prefix="/public/sellers", tags=["PublicSellers"])


@router.get("/{seller_id}", response_model=PublicSellerDTO)
async def get_seller(
    seller_id: uuid.UUID,
    service: SellerService = Depends(get_seller_service),
):
    seller = await service.get_by_id(seller_id)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    return seller
