import uuid
from abc import ABC, abstractmethod

from src.domain.entities.offer import Offer


class OfferRepository(ABC):
    @abstractmethod
    async def get_by_id(self, offer_id: uuid.UUID) -> Offer | None: ...

    @abstractmethod
    async def get_by_product(
        self, product_id: uuid.UUID, sort_by: str = "price"
    ) -> list[Offer]: ...

    @abstractmethod
    async def save(self, offer: Offer) -> Offer: ...

    @abstractmethod
    async def delete(self, offer_id: uuid.UUID) -> None: ...
