import uuid
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class CreateOfferCommand:
    product_id: uuid.UUID
    seller_id: uuid.UUID
    price_amount: Decimal
    price_currency: str
    delivery_date: date
    condition: str = "new"
    quantity: int = 1
    is_available: bool = True
    delivery_days_min: int | None = None
    delivery_days_max: int | None = None


@dataclass
class UpdateOfferCommand:
    offer_id: uuid.UUID
    seller_id: uuid.UUID | None = None
    price_amount: Decimal | None = None
    price_currency: str | None = None
    delivery_date: date | None = None
    condition: str | None = None
    quantity: int | None = None
    is_available: bool | None = None
    delivery_days_min: int | None = None
    delivery_days_max: int | None = None


@dataclass
class DeleteOfferCommand:
    offer_id: uuid.UUID
