import pytest
from unittest.mock import AsyncMock, MagicMock
import uuid

from src.domain.entities.user import User
from src.domain.entities.user_identity import UserIdentity
from src.domain.entities.product import Product
from src.domain.entities.review import Review
from src.domain.enums.user_role import UserRole
from src.domain.enums.user_status import UserStatus
from src.domain.enums.auth_provider import AuthProvider


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_user(
    role: UserRole = UserRole.USER,
    status: UserStatus = UserStatus.ACTIVE,
    first_name: str = "John",
    last_name: str = "Doe",
) -> User:
    return User(role=role, status=status, first_name=first_name, last_name=last_name)


def make_identity(
    user_id: uuid.UUID | None = None,
    email: str = "test@example.com",
    credential_hash: str = "hashed_password",
    is_verified: bool = True,
) -> UserIdentity:
    return UserIdentity(
        user_id=user_id or uuid.uuid4(),
        provider=AuthProvider.EMAIL,
        provider_id=email,
        credential_hash=credential_hash,
        is_verified=is_verified,
    )


def make_product(name: str = "Test Product", stock: int = 10) -> Product:
    from decimal import Decimal
    return Product(name=name, price_amount=Decimal("99.99"), stock=stock)


def make_review(
    product_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
    rating: int = 5,
) -> Review:
    return Review(
        product_id=product_id or uuid.uuid4(),
        user_id=user_id or uuid.uuid4(),
        author="Test User",
        rating=rating,
        text="Great product!",
    )


# ── Mock repositories ─────────────────────────────────────────────────────────

@pytest.fixture
def mock_user_repo():
    repo = MagicMock()
    repo.get_by_id = AsyncMock(return_value=None)
    repo.get_by_email = AsyncMock(return_value=None)
    repo.get_all = AsyncMock(return_value=[])
    repo.save = AsyncMock()
    repo.delete = AsyncMock()
    return repo


@pytest.fixture
def mock_identity_repo():
    repo = MagicMock()
    repo.get_by_provider = AsyncMock(return_value=None)
    repo.save = AsyncMock()
    repo.delete = AsyncMock()
    return repo


@pytest.fixture
def mock_product_repo():
    repo = MagicMock()
    repo.get_by_id = AsyncMock(return_value=None)
    repo.save = AsyncMock()
    repo.delete = AsyncMock()
    return repo


@pytest.fixture
def mock_attr_repo():
    repo = MagicMock()
    repo.get_by_product = AsyncMock(return_value=[])
    repo.save = AsyncMock()
    repo.delete_by_product = AsyncMock()
    return repo


@pytest.fixture
def mock_review_repo():
    repo = MagicMock()
    repo.get_by_user_and_product = AsyncMock(return_value=None)
    repo.save = AsyncMock()
    return repo


# ── Mock services ─────────────────────────────────────────────────────────────

@pytest.fixture
def mock_password_service():
    svc = MagicMock()
    svc.hash_password = MagicMock(return_value="hashed_password")
    svc.verify_password = MagicMock(return_value=True)
    return svc


@pytest.fixture
def mock_token_service():
    svc = MagicMock()
    svc.create_access_token = MagicMock(return_value="jwt_token")
    svc.blacklist_token = AsyncMock()
    return svc


@pytest.fixture
def mock_image_service():
    svc = MagicMock()
    svc.upload_product_image = AsyncMock(return_value=("img/key", "thumb/key"))
    svc.get_object_url = MagicMock(return_value="https://cdn.example.com/image.jpg")
    return svc
