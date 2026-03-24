import uuid

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.enums.auth_provider import AuthProvider
from src.infrastructure.database.models.base_model import BaseModel

_enum_values = lambda objs: [e.value for e in objs]


class UserIdentityModel(BaseModel):
    __tablename__ = "user_identities"

    __table_args__ = (
        UniqueConstraint("provider", "provider_id", name="uq_identity_provider_provider_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    provider: Mapped[AuthProvider] = mapped_column(
        SAEnum(AuthProvider, values_callable=_enum_values, name="authprovider"),
        nullable=False,
    )
    provider_id: Mapped[str] = mapped_column(String(255), nullable=False)
    credential_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    user: Mapped["UserModel"] = relationship(back_populates="identities")
