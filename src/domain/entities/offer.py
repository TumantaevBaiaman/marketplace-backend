import uuid
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from src.domain.entities.base import BaseEntity


@dataclass
class Offer(BaseEntity):
    product_id: uuid.UUID = field(default_factory=uuid.uuid4)
    seller_id: uuid.UUID = field(default_factory=uuid.uuid4)
    price_amount: Decimal = field(default_factory=lambda: Decimal("0"))
    price_currency: str = "USD"
    delivery_date: date = field(default_factory=date.today)
    condition: str = "new"
    quantity: int = 1
    is_available: bool = True
    delivery_days_min: int | None = None
    delivery_days_max: int | None = None
