import pytest
from src.domain.entities.user import User
from src.domain.enums.user_role import UserRole
from src.domain.enums.user_status import UserStatus


class TestUserProperties:
    def test_is_active_when_status_active(self):
        user = User(status=UserStatus.ACTIVE)
        assert user.is_active is True

    def test_is_not_active_when_banned(self):
        user = User(status=UserStatus.BANNED)
        assert user.is_active is False

    def test_is_not_active_when_pending(self):
        user = User(status=UserStatus.PENDING_VERIFICATION)
        assert user.is_active is False

    def test_is_not_active_when_inactive(self):
        user = User(status=UserStatus.INACTIVE)
        assert user.is_active is False

    def test_is_admin_when_role_admin(self):
        user = User(role=UserRole.ADMIN)
        assert user.is_admin is True

    def test_is_not_admin_when_role_user(self):
        user = User(role=UserRole.USER)
        assert user.is_admin is False

    def test_is_not_admin_when_role_moderator(self):
        user = User(role=UserRole.MODERATOR)
        assert user.is_admin is False

    def test_full_name_combines_first_and_last(self):
        user = User(first_name="John", last_name="Doe")
        assert user.full_name == "John Doe"

    def test_full_name_strips_when_last_name_empty(self):
        user = User(first_name="John", last_name="")
        assert user.full_name == "John"

    def test_full_name_empty_when_both_empty(self):
        user = User(first_name="", last_name="")
        assert user.full_name == ""


class TestUserMethods:
    def test_activate_sets_status_active(self):
        user = User(status=UserStatus.PENDING_VERIFICATION)
        user.activate()
        assert user.status == UserStatus.ACTIVE

    def test_ban_sets_status_banned(self):
        user = User(status=UserStatus.ACTIVE)
        user.ban()
        assert user.status == UserStatus.BANNED

    def test_deactivate_sets_status_inactive(self):
        user = User(status=UserStatus.ACTIVE)
        user.deactivate()
        assert user.status == UserStatus.INACTIVE

    def test_activate_then_ban(self):
        user = User(status=UserStatus.PENDING_VERIFICATION)
        user.activate()
        assert user.is_active is True
        user.ban()
        assert user.is_active is False


class TestUserEquality:
    def test_same_instance_equals_itself(self):
        user = User(first_name="John", last_name="Doe")
        assert user == user

    def test_different_instances_with_same_data_are_equal(self):
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        user1 = User(first_name="John", last_name="Doe", created_at=now, updated_at=now)
        user2 = User(first_name="John", last_name="Doe", created_at=now, updated_at=now)
        user2.id = user1.id
        assert user1 == user2

    def test_different_names_not_equal(self):
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        user1 = User(first_name="John", created_at=now, updated_at=now)
        user2 = User(first_name="Jane", created_at=now, updated_at=now)
        user2.id = user1.id
        assert user1 != user2
