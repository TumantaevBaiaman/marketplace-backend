import uuid
from dataclasses import dataclass


@dataclass
class GetProductAuditLogQuery:
    product_id: uuid.UUID
    limit: int = 50
