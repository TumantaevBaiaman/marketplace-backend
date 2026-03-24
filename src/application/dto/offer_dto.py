import uuid
from datetime import date

from pydantic import BaseModel

from src.application.dto.product_dto import MoneyDTO


class AdminOfferCreateDTO(BaseModel):
    seller_id: uuid.UUID
    price: MoneyDTO
    delivery_date: date
    condition: str = "new"
    quantity: int = 1
    is_available: bool = True
    delivery_days_min: int | None = None
    delivery_days_max: int | None = None


class AdminOfferUpdateDTO(BaseModel):
    seller_id: uuid.UUID | None = None
    price: MoneyDTO | None = None
    delivery_date: date | None = None
    condition: str | None = None
    quantity: int | None = None
    is_available: bool | None = None
    delivery_days_min: int | None = None
    delivery_days_max: int | None = None


class AdminOfferResponseDTO(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    seller_id: uuid.UUID
    seller_name: str | None = None
    price: MoneyDTO
    delivery_date: date
    condition: str = "new"
    quantity: int = 1
    is_available: bool = True
    delivery_days_min: int | None = None
    delivery_days_max: int | None = None
