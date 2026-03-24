from src.application.dto.audit_dto import AuditLogEntryDTO, AuditLogListDTO
from src.application.queries.audit_queries import GetProductAuditLogQuery
from src.domain.repositories.product_audit_log_repository import ProductAuditLogRepository


class GetProductAuditLogHandler:
    def __init__(self, repo: ProductAuditLogRepository):
        self._repo = repo

    async def handle(self, query: GetProductAuditLogQuery) -> AuditLogListDTO:
        logs = await self._repo.get_by_product(query.product_id, limit=query.limit)
        return AuditLogListDTO(
            entries=[
                AuditLogEntryDTO(
                    id=log.id,
                    product_id=log.product_id,
                    action=log.action,
                    actor_id=log.actor_id,
                    actor_email=log.actor_email,
                    diff=log.diff,
                    created_at=log.created_at,
                )
                for log in logs
            ]
        )
