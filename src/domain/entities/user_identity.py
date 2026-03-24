import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from src.domain.entities.base import BaseEntity
from src.domain.enums.auth_provider import AuthProvider


@dataclass
class UserIdentity(BaseEntity):
    """
    Способ входа пользователя.
    provider_id — уникальный идентификатор у провайдера:
      email    → адрес почты
      google   → Google sub (uid)
      apple    → Apple sub
      phone    → номер телефона
    credential_hash — хэш пароля только для EMAIL, у остальных NULL.
    """

    user_id: uuid.UUID = field(default_factory=uuid.uuid4)
    provider: AuthProvider = AuthProvider.EMAIL
    provider_id: str = ""
    credential_hash: str | None = None
    is_verified: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
