import uuid
from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class CreateSellerCommand:
    name: str
    description: str | None = None
    email: str | None = None
    phone: str | None = None
    website: str | None = None
    country: str | None = None
    rating: Decimal = field(default_factory=lambda: Decimal("5.0"))
    is_verified: bool = False


@dataclass
class UpdateSellerCommand:
    seller_id: uuid.UUID
    name: str | None = None
    description: str | None = None
    email: str | None = None
    phone: str | None = None
    website: str | None = None
    country: str | None = None
    rating: Decimal | None = None
    is_verified: bool | None = None
