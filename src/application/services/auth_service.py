from src.application.commands.auth_commands import (
    AdminLoginCommand,
    LoginCommand,
    LogoutCommand,
    RegisterCommand,
)
from src.application.handlers.command_handlers.auth_command_handlers import (
    AdminLoginHandler,
    LoginHandler,
    LogoutHandler,
    RegisterHandler,
)
from src.application.handlers.query_handlers.user_query_handlers import GetCurrentUserHandler
from src.application.queries.user_queries import GetCurrentUserQuery
from src.domain.entities.user import User
from src.domain.repositories.user_identity_repository import UserIdentityRepository
from src.domain.repositories.user_repository import UserRepository
from src.domain.services.password_service import IPasswordService
from src.domain.services.token_service import ITokenService


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        identity_repo: UserIdentityRepository,
        password_service: IPasswordService | None = None,
        token_service: ITokenService | None = None,
    ):
        self._login_handler = LoginHandler(
            user_repo, identity_repo, password_service, token_service
        )
        self._admin_login_handler = AdminLoginHandler(
            user_repo, identity_repo, password_service, token_service
        )
        self._register_handler = RegisterHandler(user_repo, identity_repo, password_service)
        self._logout_handler = LogoutHandler(token_service) if token_service else None
        self._get_me_handler = GetCurrentUserHandler(user_repo, identity_repo)

    async def login(self, command: LoginCommand) -> str:
        return await self._login_handler.handle(command)

    async def admin_login(self, command: AdminLoginCommand) -> str:
        return await self._admin_login_handler.handle(command)

    async def register(self, command: RegisterCommand) -> User:
        return await self._register_handler.handle(command)

    async def logout(self, command: LogoutCommand) -> None:
        if self._logout_handler:
            await self._logout_handler.handle(command)

    async def get_me(self, query: GetCurrentUserQuery):
        return await self._get_me_handler.handle(query)
