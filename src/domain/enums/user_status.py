from enum import StrEnum


class UserStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"
    PENDING_VERIFICATION = "pending_verification"
