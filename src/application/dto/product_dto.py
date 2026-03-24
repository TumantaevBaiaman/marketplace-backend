from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class MoneyDTO(BaseModel):
    amount: Decimal
    currency: str = "USD"


class ProductAttributeDTO(BaseModel):
    key: str
    value: str


class SellerDTO(BaseModel):
    id: uuid.UUID
    name: str
    rating: Decimal


class OfferDTO(BaseModel):
    id: uuid.UUID
    seller: SellerDTO
    price: MoneyDTO
    delivery_date: date


# Public
class ProductListItemDTO(BaseModel):
    id: uuid.UUID
    name: str
    thumbnail_url: str | None
    price: MoneyDTO
    stock: int
    nearest_delivery_date: date | None
    avg_rating: float | None = None
    review_count: int = 0


class ProductListResponseDTO(BaseModel):
    items: list[ProductListItemDTO]
    next_cursor: str | None


class ProductDetailsDTO(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None = None
    image_url: str | None
    attributes: list[ProductAttributeDTO]
    offers: list[OfferDTO]
    avg_rating: float | None = None
    review_count: int = 0
    sku: str | None = None
    min_price: MoneyDTO | None = None
    category_name: str | None = None


# Admin
class AdminProductCreateDTO(BaseModel):
    name: str
    price: MoneyDTO
    stock: int = 0
    description: str | None = None
    sku: str | None = None
    category_id: uuid.UUID | None = None
    attributes: list[ProductAttributeDTO] = []


class AdminProductUpdateDTO(BaseModel):
    name: str | None = None
    description: str | None = None
    sku: str | None = None
    category_id: uuid.UUID | None = None
    price: MoneyDTO | None = None
    stock: int | None = None
    is_active: bool | None = None
    attributes: list[ProductAttributeDTO] | None = None


class AdminProductResponseDTO(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None = None
    sku: str | None = None
    category_id: uuid.UUID | None = None
    price: MoneyDTO
    stock: int
    is_active: bool = True
    image_url: str | None
    thumbnail_url: str | None
    attributes: list[ProductAttributeDTO]
