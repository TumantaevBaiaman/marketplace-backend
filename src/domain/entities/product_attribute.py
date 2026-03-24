import uuid
from dataclasses import dataclass, field

from src.domain.entities.base import BaseEntity


@dataclass
class ProductAttribute(BaseEntity):
    product_id: uuid.UUID = field(default_factory=uuid.uuid4)
    key: str = ""
    value: str = ""
