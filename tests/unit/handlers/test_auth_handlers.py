import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock

from src.application.handlers.command_handlers.auth_command_handlers import (
    LoginHandler,
    AdminLoginHandler,
    RegisterHandler,
    LogoutHandler,
)
from src.application.commands.auth_commands import (
    LoginCommand,
    AdminLoginCommand,
    RegisterCommand,
    LogoutCommand,
)
from src.domain.exceptions.domain_exceptions import AccessDenied, EntityAlreadyExists
from src.domain.enums.user_role import UserRole
from src.domain.enums.user_status import UserStatus
from tests.conftest import make_user, make_identity


# ── LoginHandler ──────────────────────────────────────────────────────────────

class TestLoginHandler:
    def _handler(self, user_repo, identity_repo, password_svc, token_svc):
        return LoginHandler(user_repo, identity_repo, password_svc, token_svc)

    @pytest.mark.asyncio
    async def test_returns_token_on_valid_credentials(
        self, mock_user_repo, mock_identity_repo, mock_password_service, mock_token_service
    ):
        user = make_user(status=UserStatus.ACTIVE)
        identity = make_identity(user_id=user.id, is_verified=True)
        mock_identity_repo.get_by_provider = AsyncMock(return_value=identity)
        mock_user_repo.get_by_id = AsyncMock(return_value=user)
        mock_password_service.verify_password = MagicMock(return_value=True)
        mock_token_service.create_access_token = MagicMock(return_value="valid_token")

        handler = self._handler(mock_user_repo, mock_identity_repo, mock_password_service, mock_token_service)
        token = await handler.handle(LoginCommand(email="test@example.com", password="secret"))

        assert token == "valid_token"

    @pytest.mark.asyncio
    async def test_raises_when_identity_not_found(
        self, mock_user_repo, mock_identity_repo, mock_password_service, mock_token_service
    ):
        mock_identity_repo.get_by_provider = AsyncMock(return_value=None)

        handler = self._handler(mock_user_repo, mock_identity_repo, mock_password_service, mock_token_service)
        with pytest.raises(AccessDenied):
            await handler.handle(LoginCommand(email="no@example.com", password="x"))

    @pytest.mark.asyncio
    async def test_raises_when_wrong_password(
        self, mock_user_repo, mock_identity_repo, mock_password_service, mock_token_service
    ):
        identity = make_identity(is_verified=True)
        mock_identity_repo.get_by_provider = AsyncMock(return_value=identity)
        mock_password_service.verify_password = MagicMock(return_value=False)

        handler = self._handler(mock_user_repo, mock_identity_repo, mock_password_service, mock_token_service)
        with pytest.raises(AccessDenied):
            await handler.handle(LoginCommand(email="test@example.com", password="wrong"))

    @pytest.mark.asyncio
    async def test_raises_when_email_not_verified(
        self, mock_user_repo, mock_identity_repo, mock_password_service, mock_token_service
    ):
        identity = make_identity(is_verified=False)
        mock_identity_repo.get_by_provider = AsyncMock(return_value=identity)
        mock_password_service.verify_password = MagicMock(return_value=True)

        handler = self._handler(mock_user_repo, mock_identity_repo, mock_password_service, mock_token_service)
        with pytest.raises(AccessDenied):
            await handler.handle(LoginCommand(email="test@example.com", password="secret"))

    @pytest.mark.asyncio
    async def test_raises_when_user_is_banned(
        self, mock_user_repo, mock_identity_repo, mock_password_service, mock_token_service
    ):
        user = make_user(status=UserStatus.BANNED)
        identity = make_identity(user_id=user.id, is_verified=True)
        mock_identity_repo.get_by_provider = AsyncMock(return_value=identity)
        mock_user_repo.get_by_id = AsyncMock(return_value=user)
        mock_password_service.verify_password = MagicMock(return_value=True)

        handler = self._handler(mock_user_repo, mock_identity_repo, mock_password_service, mock_token_service)
        with pytest.raises(AccessDenied):
            await handler.handle(LoginCommand(email="test@example.com", password="secret"))


# ── AdminLoginHandler ─────────────────────────────────────────────────────────

class TestAdminLoginHandler:
    def _handler(self, user_repo, identity_repo, password_svc, token_svc):
        return AdminLoginHandler(user_repo, identity_repo, password_svc, token_svc)

    @pytest.mark.asyncio
    async def test_admin_can_login(
        self, mock_user_repo, mock_identity_repo, mock_password_service, mock_token_service
    ):
        user = make_user(role=UserRole.ADMIN, status=UserStatus.ACTIVE)
        identity = make_identity(user_id=user.id, is_verified=True)
        mock_identity_repo.get_by_provider = AsyncMock(return_value=identity)
        mock_user_repo.get_by_id = AsyncMock(return_value=user)
        mock_password_service.verify_password = MagicMock(return_value=True)
        mock_token_service.create_access_token = MagicMock(return_value="admin_token")

        handler = self._handler(mock_user_repo, mock_identity_repo, mock_password_service, mock_token_service)
        token = await handler.handle(AdminLoginCommand(email="admin@example.com", password="secret"))

        assert token == "admin_token"

    @pytest.mark.asyncio
    async def test_moderator_can_login(
        self, mock_user_repo, mock_identity_repo, mock_password_service, mock_token_service
    ):
        user = make_user(role=UserRole.MODERATOR, status=UserStatus.ACTIVE)
        identity = make_identity(user_id=user.id, is_verified=True)
        mock_identity_repo.get_by_provider = AsyncMock(return_value=identity)
        mock_user_repo.get_by_id = AsyncMock(return_value=user)
        mock_password_service.verify_password = MagicMock(return_value=True)

        handler = self._handler(mock_user_repo, mock_identity_repo, mock_password_service, mock_token_service)
        token = await handler.handle(AdminLoginCommand(email="mod@example.com", password="secret"))

        assert token is not None

    @pytest.mark.asyncio
    async def test_regular_user_cannot_login_to_admin(
        self, mock_user_repo, mock_identity_repo, mock_password_service, mock_token_service
    ):
        user = make_user(role=UserRole.USER, status=UserStatus.ACTIVE)
        identity = make_identity(user_id=user.id, is_verified=True)
        mock_identity_repo.get_by_provider = AsyncMock(return_value=identity)
        mock_user_repo.get_by_id = AsyncMock(return_value=user)
        mock_password_service.verify_password = MagicMock(return_value=True)

        handler = self._handler(mock_user_repo, mock_identity_repo, mock_password_service, mock_token_service)
        with pytest.raises(AccessDenied):
            await handler.handle(AdminLoginCommand(email="user@example.com", password="secret"))

    @pytest.mark.asyncio
    async def test_raises_when_admin_is_banned(
        self, mock_user_repo, mock_identity_repo, mock_password_service, mock_token_service
    ):
        user = make_user(role=UserRole.ADMIN, status=UserStatus.BANNED)
        identity = make_identity(user_id=user.id, is_verified=True)
        mock_identity_repo.get_by_provider = AsyncMock(return_value=identity)
        mock_user_repo.get_by_id = AsyncMock(return_value=user)
        mock_password_service.verify_password = MagicMock(return_value=True)

        handler = self._handler(mock_user_repo, mock_identity_repo, mock_password_service, mock_token_service)
        with pytest.raises(AccessDenied):
            await handler.handle(AdminLoginCommand(email="admin@example.com", password="secret"))


# ── RegisterHandler ───────────────────────────────────────────────────────────

class TestRegisterHandler:
    def _handler(self, user_repo, identity_repo, password_svc):
        return RegisterHandler(user_repo, identity_repo, password_svc)

    @pytest.mark.asyncio
    async def test_register_creates_user_and_identity(
        self, mock_user_repo, mock_identity_repo, mock_password_service
    ):
        mock_identity_repo.get_by_provider = AsyncMock(return_value=None)

        handler = self._handler(mock_user_repo, mock_identity_repo, mock_password_service)
        user = await handler.handle(RegisterCommand(
            email="new@example.com",
            password="secret",
            first_name="Jane",
            last_name="Smith",
        ))

        mock_user_repo.save.assert_called_once()
        mock_identity_repo.save.assert_called_once()
        assert user.first_name == "Jane"
        assert user.last_name == "Smith"

    @pytest.mark.asyncio
    async def test_register_sets_pending_status(
        self, mock_user_repo, mock_identity_repo, mock_password_service
    ):
        mock_identity_repo.get_by_provider = AsyncMock(return_value=None)

        handler = self._handler(mock_user_repo, mock_identity_repo, mock_password_service)
        user = await handler.handle(RegisterCommand(
            email="new@example.com",
            password="secret",
            first_name="Jane",
            last_name="Smith",
        ))

        assert user.status == UserStatus.PENDING_VERIFICATION

    @pytest.mark.asyncio
    async def test_register_sets_user_role(
        self, mock_user_repo, mock_identity_repo, mock_password_service
    ):
        mock_identity_repo.get_by_provider = AsyncMock(return_value=None)

        handler = self._handler(mock_user_repo, mock_identity_repo, mock_password_service)
        user = await handler.handle(RegisterCommand(
            email="new@example.com",
            password="secret",
            first_name="Jane",
            last_name="Smith",
        ))

        assert user.role == UserRole.USER

    @pytest.mark.asyncio
    async def test_register_raises_when_email_already_exists(
        self, mock_user_repo, mock_identity_repo, mock_password_service
    ):
        existing = make_identity(email="existing@example.com")
        mock_identity_repo.get_by_provider = AsyncMock(return_value=existing)

        handler = self._handler(mock_user_repo, mock_identity_repo, mock_password_service)
        with pytest.raises(EntityAlreadyExists):
            await handler.handle(RegisterCommand(
                email="existing@example.com",
                password="secret",
                first_name="Jane",
                last_name="Smith",
            ))

    @pytest.mark.asyncio
    async def test_register_hashes_password(
        self, mock_user_repo, mock_identity_repo, mock_password_service
    ):
        mock_identity_repo.get_by_provider = AsyncMock(return_value=None)
        mock_password_service.hash_password = MagicMock(return_value="$bcrypt$hash")

        handler = self._handler(mock_user_repo, mock_identity_repo, mock_password_service)
        await handler.handle(RegisterCommand(
            email="new@example.com",
            password="plaintext",
            first_name="Jane",
            last_name="Smith",
        ))

        mock_password_service.hash_password.assert_called_once_with("plaintext")


# ── LogoutHandler ─────────────────────────────────────────────────────────────

class TestLogoutHandler:
    @pytest.mark.asyncio
    async def test_logout_blacklists_token(self, mock_token_service):
        handler = LogoutHandler(mock_token_service)
        await handler.handle(LogoutCommand(jti="some-jti", ttl_seconds=3600))

        mock_token_service.blacklist_token.assert_called_once_with("some-jti", 3600)
