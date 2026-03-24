import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from src.domain.entities.base import BaseEntity


@dataclass
class Review(BaseEntity):
    product_id: uuid.UUID = field(default_factory=uuid.uuid4)
    user_id: uuid.UUID = field(default_factory=uuid.uuid4)
    author: str = ""
    rating: int = 5
    text: str = ""
    is_verified_purchase: bool = False
    helpful_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
