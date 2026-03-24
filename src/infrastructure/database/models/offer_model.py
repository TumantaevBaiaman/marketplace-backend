import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, Integer, Numeric
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.enums.currency import Currency
from src.domain.enums.offer_condition import OfferCondition
from src.infrastructure.database.models.base_model import BaseModel

_enum_values = lambda objs: [e.value for e in objs]


class OfferModel(BaseModel):
    __tablename__ = "offers"

    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    seller_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sellers.id", ondelete="CASCADE"), nullable=False, index=True
    )

    price_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    price_currency: Mapped[Currency] = mapped_column(
        SAEnum(Currency, values_callable=_enum_values, name="currency"),
        nullable=False,
        default=Currency.USD,
    )

    condition: Mapped[OfferCondition] = mapped_column(
        SAEnum(OfferCondition, values_callable=_enum_values, name="offercondition"),
        nullable=False,
        default=OfferCondition.NEW,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    delivery_date: Mapped[date] = mapped_column(Date, nullable=False)
    delivery_days_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    delivery_days_max: Mapped[int | None] = mapped_column(Integer, nullable=True)

    product: Mapped["ProductModel"] = relationship(back_populates="offers")
    seller: Mapped["SellerModel"] = relationship(back_populates="offers")
