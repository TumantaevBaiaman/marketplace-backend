import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.models.base_model import BaseModel


class CategoryModel(BaseModel):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    icon_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True
    )

    parent: Mapped["CategoryModel | None"] = relationship(
        back_populates="children", remote_side="CategoryModel.id"
    )
    children: Mapped[list["CategoryModel"]] = relationship(
        back_populates="parent", cascade="all, delete-orphan"
    )
    products: Mapped[list["ProductModel"]] = relationship(back_populates="category")
