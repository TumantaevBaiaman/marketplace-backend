import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.models.base_model import BaseModel


class ReviewModel(BaseModel):
    __tablename__ = "reviews"
    __table_args__ = (UniqueConstraint("user_id", "product_id", name="uq_review_user_product"),)

    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    author: Mapped[str] = mapped_column(String(200), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1–5
    text: Mapped[str] = mapped_column(Text, nullable=False, default="")

    is_verified_purchase: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    helpful_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    product: Mapped["ProductModel"] = relationship(back_populates="reviews")
