from src.application.commands.auth_commands import (
    AdminLoginCommand,
    LoginCommand,
    LogoutCommand,
    RegisterCommand,
)
from src.domain.entities.user import User
from src.domain.entities.user_identity import UserIdentity
from src.domain.enums.auth_provider import AuthProvider
from src.domain.enums.user_role import UserRole
from src.domain.enums.user_status import UserStatus
from src.domain.exceptions.domain_exceptions import AccessDenied, EntityAlreadyExists
from src.domain.repositories.user_identity_repository import UserIdentityRepository
from src.domain.repositories.user_repository import UserRepository
from src.domain.services.password_service import IPasswordService
from src.domain.services.token_service import ITokenService


class LoginHandler:
    def __init__(
        self,
        user_repo: UserRepository,
        identity_repo: UserIdentityRepository,
        password_service: IPasswordService,
        token_service: ITokenService,
    ):
        self._user_repo = user_repo
        self._identity_repo = identity_repo
        self._password_service = password_service
        self._token_service = token_service

    async def handle(self, command: LoginCommand) -> str:
        identity = await self._identity_repo.get_by_provider(
            provider=AuthProvider.EMAIL,
            provider_id=command.email,
        )
        if not identity:
            raise AccessDenied("Invalid credentials")

        if not self._password_service.verify_password(
            command.password, identity.credential_hash or ""
        ):
            raise AccessDenied("Invalid credentials")

        if not identity.is_verified:
            raise AccessDenied("Email is not verified")

        user = await self._user_repo.get_by_id(identity.user_id)

        if not user.is_active:
            raise AccessDenied("Account is suspended")

        return self._token_service.create_access_token(
            {
                "sub": str(user.id),
                "role": user.role,
                "status": user.status,
            }
        )


class AdminLoginHandler:
    def __init__(
        self,
        user_repo: UserRepository,
        identity_repo: UserIdentityRepository,
        password_service: IPasswordService,
        token_service: ITokenService,
    ):
        self._user_repo = user_repo
        self._identity_repo = identity_repo
        self._password_service = password_service
        self._token_service = token_service

    async def handle(self, command: AdminLoginCommand) -> str:
        identity = await self._identity_repo.get_by_provider(
            provider=AuthProvider.EMAIL,
            provider_id=command.email,
        )
        if not identity:
            raise AccessDenied("Invalid credentials")

        if not self._password_service.verify_password(
            command.password, identity.credential_hash or ""
        ):
            raise AccessDenied("Invalid credentials")

        user = await self._user_repo.get_by_id(identity.user_id)

        if user.role not in (UserRole.ADMIN, UserRole.MODERATOR):
            raise AccessDenied("Admin access required")

        if not user.is_active:
            raise AccessDenied("Account is suspended")

        return self._token_service.create_access_token(
            {
                "sub": str(user.id),
                "email": command.email,
                "role": user.role,
                "status": user.status,
            }
        )


class RegisterHandler:
    def __init__(
        self,
        user_repo: UserRepository,
        identity_repo: UserIdentityRepository,
        password_service: IPasswordService,
    ):
        self._user_repo = user_repo
        self._identity_repo = identity_repo
        self._password_service = password_service

    async def handle(self, command: RegisterCommand) -> User:
        existing = await self._identity_repo.get_by_provider(
            provider=AuthProvider.EMAIL,
            provider_id=command.email,
        )
        if existing:
            raise EntityAlreadyExists("Email already registered")

        user = User(
            first_name=command.first_name,
            last_name=command.last_name,
            role=UserRole.USER,
            status=UserStatus.PENDING_VERIFICATION,
        )
        await self._user_repo.save(user)

        identity = UserIdentity(
            user_id=user.id,
            provider=AuthProvider.EMAIL,
            provider_id=command.email,
            credential_hash=self._password_service.hash_password(command.password),
            is_verified=False,
        )
        await self._identity_repo.save(identity)

        return user


class LogoutHandler:
    def __init__(self, token_service: ITokenService):
        self._token_service = token_service

    async def handle(self, command: LogoutCommand) -> None:
        await self._token_service.blacklist_token(command.jti, command.ttl_seconds)
