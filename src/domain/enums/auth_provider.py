from enum import StrEnum


class AuthProvider(StrEnum):
    EMAIL = "email"
    GOOGLE = "google"
    APPLE = "apple"
    PHONE = "phone"
