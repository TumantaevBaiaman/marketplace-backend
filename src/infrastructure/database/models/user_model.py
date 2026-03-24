from sqlalchemy import Enum as SAEnum
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.enums.user_role import UserRole
from src.domain.enums.user_status import UserStatus
from src.infrastructure.database.models.base_model import BaseModel

_enum_values = lambda objs: [e.value for e in objs]


class UserModel(BaseModel):
    __tablename__ = "users"

    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, values_callable=_enum_values, name="userrole"),
        nullable=False,
        default=UserRole.USER,
    )
    status: Mapped[UserStatus] = mapped_column(
        SAEnum(UserStatus, values_callable=_enum_values, name="userstatus"),
        nullable=False,
        default=UserStatus.PENDING_VERIFICATION,
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    last_name: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    identities: Mapped[list["UserIdentityModel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
