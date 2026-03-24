import uuid
from abc import ABC, abstractmethod

from src.domain.entities.product import Product


class ProductRepository(ABC):
    @abstractmethod
    async def get_by_id(self, product_id: uuid.UUID) -> Product | None: ...

    @abstractmethod
    async def get_list(
        self,
        limit: int,
        cursor: uuid.UUID | None,
        in_stock: bool = False,
        sort: str = "default",
        search: str | None = None,
        is_active: bool | None = None,
        price_min: float | None = None,
        price_max: float | None = None,
    ) -> tuple[list[Product], uuid.UUID | None]: ...

    @abstractmethod
    async def save(self, product: Product) -> Product: ...

    @abstractmethod
    async def delete(self, product_id: uuid.UUID) -> None: ...

    @abstractmethod
    async def get_ratings(
        self, product_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, tuple[float | None, int]]: ...

    @abstractmethod
    async def get_category_name(self, category_id: uuid.UUID) -> str | None: ...

    @abstractmethod
    async def count(self) -> int: ...
