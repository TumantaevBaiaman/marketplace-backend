import uuid
from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class CreateProductCommand:
    name: str
    price_amount: Decimal = Decimal("0")
    price_currency: str = "USD"
    stock: int = 0
    description: str | None = None
    sku: str | None = None
    category_id: uuid.UUID | None = None
    attributes: list[dict] = field(default_factory=list)
    actor_id: uuid.UUID | None = None
    actor_email: str | None = None


@dataclass
class UpdateProductCommand:
    product_id: uuid.UUID
    name: str | None = None
    description: str | None = None
    sku: str | None = None
    category_id: uuid.UUID | None = None
    price_amount: Decimal | None = None
    price_currency: str | None = None
    stock: int | None = None
    is_active: bool | None = None
    attributes: list[dict] | None = None
    actor_id: uuid.UUID | None = None
    actor_email: str | None = None


@dataclass
class DeleteProductCommand:
    product_id: uuid.UUID
    actor_id: uuid.UUID | None = None
    actor_email: str | None = None


@dataclass
class UploadProductImageCommand:
    product_id: uuid.UUID
    data: bytes
    content_type: str
