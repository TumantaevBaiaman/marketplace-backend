import uuid
from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.enums.currency import Currency
from src.infrastructure.database.models.base_model import BaseModel

_enum_values = lambda objs: [e.value for e in objs]


class ProductModel(BaseModel):
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True
    )
    sku: Mapped[str | None] = mapped_column(String(100), nullable=True, unique=True)
    price_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    price_currency: Mapped[Currency] = mapped_column(
        SAEnum(Currency, values_callable=_enum_values, name="currency"),
        nullable=False,
        default=Currency.USD,
    )
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    views_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    image_object_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    thumbnail_object_key: Mapped[str | None] = mapped_column(String(500), nullable=True)

    category: Mapped["CategoryModel | None"] = relationship(back_populates="products")

    attributes: Mapped[list["ProductAttributeModel"]] = relationship(
        back_populates="product", cascade="all, delete-orphan", lazy="selectin"
    )
    offers: Mapped[list["OfferModel"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
    reviews: Mapped[list["ReviewModel"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
