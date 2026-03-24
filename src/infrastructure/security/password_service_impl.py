from src.domain.services.password_service import IPasswordService
from src.infrastructure.security.password import hash_password, verify_password


class PasswordServiceImpl(IPasswordService):
    def hash_password(self, password: str) -> str:
        return hash_password(password)

    def verify_password(self, plain: str, hashed: str) -> bool:
        return verify_password(plain, hashed)
