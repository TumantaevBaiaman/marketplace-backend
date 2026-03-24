import uuid
from dataclasses import dataclass


@dataclass
class CreateReviewCommand:
    product_id: uuid.UUID
    user_id: uuid.UUID
    author: str
    rating: int
    text: str
