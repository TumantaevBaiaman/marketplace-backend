import uuid
from abc import ABC, abstractmethod

from src.domain.entities.review import Review


class ReviewRepository(ABC):
    @abstractmethod
    async def get_by_product(self, product_id: uuid.UUID) -> list[Review]: ...

    @abstractmethod
    async def get_by_user_and_product(
        self, user_id: uuid.UUID, product_id: uuid.UUID
    ) -> Review | None: ...

    @abstractmethod
    async def save(self, review: Review) -> Review: ...
