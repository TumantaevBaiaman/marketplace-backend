import uuid
from dataclasses import dataclass


@dataclass
class ListPublicProductsQuery:
    limit: int
    cursor: str | None
    in_stock: bool = False
    sort: str = "default"


@dataclass
class GetPublicProductDetailsQuery:
    product_id: uuid.UUID
    offers_sort: str = "price"


@dataclass
class AdminListProductsQuery:
    limit: int
    cursor: str | None
    sort: str = "default"
    search: str | None = None
    is_active: bool | None = None
    in_stock: bool = False
    price_min: float | None = None
    price_max: float | None = None


@dataclass
class AdminGetProductQuery:
    product_id: uuid.UUID
