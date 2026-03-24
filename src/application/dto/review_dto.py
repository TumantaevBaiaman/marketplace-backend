import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ReviewCreateDTO(BaseModel):
    author: str = Field(min_length=1, max_length=200)
    rating: int = Field(ge=1, le=5)
    text: str = Field(default="", max_length=2000)


class ReviewResponseDTO(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    user_id: uuid.UUID
    author: str
    rating: int
    text: str
    created_at: datetime


class ReviewListDTO(BaseModel):
    items: list[ReviewResponseDTO]
    total: int
    avg_rating: float | None
