import uuid
from decimal import Decimal

from pydantic import BaseModel, Field


class AdminSellerCreateDTO(BaseModel):
    name: str
    description: str | None = None
    email: str | None = None
    phone: str | None = None
    website: str | None = None
    country: str | None = None
    rating: Decimal = Field(default=Decimal("5.0"), ge=Decimal("1"), le=Decimal("5"))
    is_verified: bool = False


class AdminSellerUpdateDTO(BaseModel):
    name: str | None = None
    description: str | None = None
    email: str | None = None
    phone: str | None = None
    website: str | None = None
    country: str | None = None
    rating: Decimal | None = Field(default=None, ge=Decimal("1"), le=Decimal("5"))
    is_verified: bool | None = None


class AdminSellerResponseDTO(BaseModel):
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
