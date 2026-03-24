from dataclasses import dataclass, field
from datetime import datetime, timezone

from src.domain.entities.base import BaseEntity
from src.domain.enums.user_role import UserRole
from src.domain.enums.user_status import UserStatus


@dataclass
class User(BaseEntity):
    """
    Aggregate root. Не хранит пароль/email напрямую —
    вся аутентификация вынесена в UserIdentity.
    Один пользователь может иметь несколько identity (email, google, phone).
    """

    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.PENDING_VERIFICATION
    first_name: str = ""
    last_name: str = ""
    avatar_url: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_active(self) -> bool:
        return self.status == UserStatus.ACTIVE

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    def activate(self) -> None:
        self.status = UserStatus.ACTIVE

    def ban(self) -> None:
        self.status = UserStatus.BANNED

    def deactivate(self) -> None:
        self.status = UserStatus.INACTIVE
