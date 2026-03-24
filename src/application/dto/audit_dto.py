from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class AuditLogEntryDTO(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    action: str
    actor_id: uuid.UUID | None
    actor_email: str | None
    diff: dict
    created_at: datetime


class AuditLogListDTO(BaseModel):
    entries: list[AuditLogEntryDTO]
