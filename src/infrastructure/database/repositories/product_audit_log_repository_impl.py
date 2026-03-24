import uuid

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.product_audit_log import ProductAuditLog
from src.domain.repositories.product_audit_log_repository import ProductAuditLogRepository
from src.infrastructure.database.filters import apply_filters
from src.infrastructure.database.models.product_audit_log_model import ProductAuditLogModel


class SQLAlchemyProductAuditLogRepository(ProductAuditLogRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, log: ProductAuditLog) -> None:
        model = ProductAuditLogModel(
            id=log.id,
            product_id=log.product_id,
            action=log.action,
            actor_id=log.actor_id,
            actor_email=log.actor_email,
            diff=log.diff,
            created_at=log.created_at,
        )
        self._session.add(model)
        await self._session.commit()

    async def get_by_product(
        self,
        product_id: uuid.UUID,
        limit: int = 50,
    ) -> list[ProductAuditLog]:
        q = (
            select(ProductAuditLogModel)
            .order_by(desc(ProductAuditLogModel.created_at))
            .limit(limit)
        )
        q = apply_filters(q, ProductAuditLogModel, {"product_id": product_id})
        result = await self._session.execute(q)
        return [self._to_entity(r) for r in result.scalars().all()]

    @staticmethod
    def _to_entity(m: ProductAuditLogModel) -> ProductAuditLog:
        return ProductAuditLog(
            id=m.id,
            product_id=m.product_id,
            action=m.action,
            actor_id=m.actor_id,
            actor_email=m.actor_email,
            diff=m.diff,
            created_at=m.created_at,
        )
