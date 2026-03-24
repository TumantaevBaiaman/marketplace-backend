import uuid
from abc import ABC, abstractmethod

from src.domain.entities.seller import Seller


class SellerRepository(ABC):
    @abstractmethod
    async def get_by_id(self, seller_id: uuid.UUID) -> Seller | None: ...

    @abstractmethod
    async def get_all(self) -> list[Seller]: ...

    @abstractmethod
    async def save(self, seller: Seller) -> Seller: ...
