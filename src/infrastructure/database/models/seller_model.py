from decimal import Decimal

from sqlalchemy import Boolean, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.models.base_model import BaseModel


class SellerModel(BaseModel):
    __tablename__ = "sellers"

    name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)

    rating: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False, default=Decimal("5.0"))
    review_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    offers: Mapped[list["OfferModel"]] = relationship(back_populates="seller")
