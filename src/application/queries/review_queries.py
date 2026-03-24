import uuid
from dataclasses import dataclass


@dataclass
class ListReviewsQuery:
    product_id: uuid.UUID


@dataclass
class GetMyReviewQuery:
    product_id: uuid.UUID
    user_id: uuid.UUID
