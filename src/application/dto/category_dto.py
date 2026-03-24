import uuid

from pydantic import BaseModel


class CategoryDTO(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    parent_id: uuid.UUID | None = None

    class Config:
        from_attributes = True
