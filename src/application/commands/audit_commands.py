import uuid
from dataclasses import dataclass


@dataclass
class WriteProductAuditLogCommand:
    product_id: uuid.UUID
    action: str
    diff: dict
    actor_id: uuid.UUID | None = None
    actor_email: str | None = None
