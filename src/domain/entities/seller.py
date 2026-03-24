from dataclasses import dataclass, field
from decimal import Decimal

from src.domain.entities.base import BaseEntity


@dataclass
class Seller(BaseEntity):
    name: str = ""
    description: str | None = None
    email: str | None = None
    phone: str | None = None
    website: str | None = None
    country: str | None = None
    rating: Decimal = field(default_factory=lambda: Decimal("5.0"))
    review_count: int = 0
    is_verified: bool = False
