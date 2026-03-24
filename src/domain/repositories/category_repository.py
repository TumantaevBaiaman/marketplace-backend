from abc import ABC, abstractmethod

from src.domain.entities.category import Category


class CategoryRepository(ABC):
    @abstractmethod
    async def get_all(self) -> list[Category]: ...
