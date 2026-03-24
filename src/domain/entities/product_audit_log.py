import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ProductAuditLog:
    product_id: uuid.UUID
    action: str  # 'create' | 'update' | 'delete' | 'upload_image'
    diff: dict  # {"field": {"before": ..., "after": ...}}
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    actor_id: uuid.UUID | None = None
    actor_email: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
