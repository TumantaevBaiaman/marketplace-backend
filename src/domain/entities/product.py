import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal

from src.domain.entities.base import BaseEntity


@dataclass
class Product(BaseEntity):
    name: str = ""
    description: str | None = None
    sku: str | None = None
    category_id: uuid.UUID | None = None
    price_amount: Decimal = field(default_factory=lambda: Decimal("0"))
    price_currency: str = "USD"
    stock: int = 0
    is_active: bool = True
    image_object_key: str | None = None
    thumbnail_object_key: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
