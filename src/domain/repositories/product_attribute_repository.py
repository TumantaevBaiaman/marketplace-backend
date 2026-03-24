import uuid
from abc import ABC, abstractmethod

from src.domain.entities.product_attribute import ProductAttribute


class ProductAttributeRepository(ABC):
    @abstractmethod
    async def get_by_product(self, product_id: uuid.UUID) -> list[ProductAttribute]: ...

    @abstractmethod
    async def save(self, attr: ProductAttribute) -> ProductAttribute: ...

    @abstractmethod
    async def delete_by_product(self, product_id: uuid.UUID) -> None: ...
