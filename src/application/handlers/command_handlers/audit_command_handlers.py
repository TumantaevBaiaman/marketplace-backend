from src.application.commands.audit_commands import WriteProductAuditLogCommand
from src.domain.entities.product_audit_log import ProductAuditLog
from src.domain.repositories.product_audit_log_repository import ProductAuditLogRepository


class WriteProductAuditLogHandler:
    def __init__(self, repo: ProductAuditLogRepository):
        self._repo = repo

    async def handle(self, command: WriteProductAuditLogCommand) -> None:
        log = ProductAuditLog(
            product_id=command.product_id,
            action=command.action,
            diff=command.diff,
            actor_id=command.actor_id,
            actor_email=command.actor_email,
        )
        await self._repo.save(log)
