import uuid
from abc import ABC, abstractmethod

from src.domain.entities.product_audit_log import ProductAuditLog


class ProductAuditLogRepository(ABC):
    @abstractmethod
    async def save(self, log: ProductAuditLog) -> None: ...

    @abstractmethod
    async def get_by_product(
        self,
        product_id: uuid.UUID,
        limit: int = 50,
    ) -> list[ProductAuditLog]: ...
