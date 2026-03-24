import uuid
from dataclasses import dataclass


@dataclass
class GetOffersByProductQuery:
    product_id: uuid.UUID
