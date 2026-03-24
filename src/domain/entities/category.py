import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from src.domain.entities.base import BaseEntity


@dataclass
class Category(BaseEntity):
    name: str = ""
    slug: str = ""
    description: str | None = None
    icon_url: str | None = None
    parent_id: uuid.UUID | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
