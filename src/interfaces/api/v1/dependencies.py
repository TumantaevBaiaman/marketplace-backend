import jwt
from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.services.auth_service import AuthService
from src.application.services.user_service import UserService
from src.domain.enums.user_role import UserRole
from src.domain.exceptions.domain_exceptions import AccessDenied
from src.infrastructure.cache.cache import get_redis
from src.infrastructure.cache.token_blacklist import is_token_blacklisted
from src.infrastructure.database.base import async_session_maker
from src.infrastructure.database.repositories.user_identity_repository_impl import (
    SQLAlchemyUserIdentityRepository,
)
from src.infrastructure.database.repositories.user_repository_impl import SQLAlchemyUserRepository
from src.infrastructure.security.jwt_service import decode_token
from src.infrastructure.security.password_service_impl import PasswordServiceImpl
from src.infrastructure.security.token_service_impl import TokenServiceImpl
from src.infrastructure.storage.image_service_impl import ImageServiceImpl

_bearer = HTTPBearer()

_password_service = PasswordServiceImpl()


async def get_session():
    async with async_session_maker() as session:
        yield session


async def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    return UserService(SQLAlchemyUserRepository(session))


async def get_auth_service(
    session: AsyncSession = Depends(get_session),
    redis=Depends(get_redis),
) -> AuthService:
    token_service = TokenServiceImpl(redis)
    return AuthService(
        SQLAlchemyUserRepository(session),
        SQLAlchemyUserIdentityRepository(session),
        password_service=_password_service,
        token_service=token_service,
    )


def _extract_payload(credentials: HTTPAuthorizationCredentials) -> dict:
    try:
        return decode_token(credentials.credentials)
    except jwt.ExpiredSignatureError:
        raise AccessDenied("Token expired")
    except jwt.InvalidTokenError:
        raise AccessDenied("Invalid token")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(_bearer),
    redis=Depends(get_redis),
) -> dict:
    payload = _extract_payload(credentials)
    jti = payload.get("jti")
    if jti and await is_token_blacklisted(redis, jti):
        raise AccessDenied("Token has been revoked")
    return payload


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Security(_bearer),
    redis=Depends(get_redis),
) -> dict:
    payload = _extract_payload(credentials)
    jti = payload.get("jti")
    if jti and await is_token_blacklisted(redis, jti):
        raise AccessDenied("Token has been revoked")
    if payload.get("role") != UserRole.ADMIN:
        raise AccessDenied("Admin access required")
    return payload


async def get_current_moderator_or_admin(
    credentials: HTTPAuthorizationCredentials = Security(_bearer),
    redis=Depends(get_redis),
) -> dict:
    payload = _extract_payload(credentials)
    jti = payload.get("jti")
    if jti and await is_token_blacklisted(redis, jti):
        raise AccessDenied("Token has been revoked")
    if payload.get("role") not in (UserRole.ADMIN, UserRole.MODERATOR):
        raise AccessDenied("Insufficient permissions")
    return payload


async def get_product_service(session: AsyncSession = Depends(get_session)):
    from src.application.services.product_service import ProductService
    from src.infrastructure.database.repositories.offer_repository_impl import (
        SQLAlchemyOfferRepository,
    )
    from src.infrastructure.database.repositories.product_attribute_repository_impl import (
        SQLAlchemyProductAttributeRepository,
    )
    from src.infrastructure.database.repositories.product_audit_log_repository_impl import (
        SQLAlchemyProductAuditLogRepository,
    )
    from src.infrastructure.database.repositories.product_repository_impl import (
        SQLAlchemyProductRepository,
    )
    from src.infrastructure.database.repositories.seller_repository_impl import (
        SQLAlchemySellerRepository,
    )

    image_service = ImageServiceImpl()
    return ProductService(
        SQLAlchemyProductRepository(session),
        SQLAlchemyProductAttributeRepository(session),
        SQLAlchemyOfferRepository(session),
        SQLAlchemySellerRepository(session),
        SQLAlchemyProductAuditLogRepository(session),
        image_service=image_service,
    )


async def get_seller_service(session: AsyncSession = Depends(get_session)):
    from src.application.services.seller_service import SellerService
    from src.infrastructure.database.repositories.seller_repository_impl import (
        SQLAlchemySellerRepository,
    )

    return SellerService(SQLAlchemySellerRepository(session))


async def get_offer_service(session: AsyncSession = Depends(get_session)):
    from src.application.services.offer_service import OfferService
    from src.infrastructure.database.repositories.offer_repository_impl import (
        SQLAlchemyOfferRepository,
    )
    from src.infrastructure.database.repositories.seller_repository_impl import (
        SQLAlchemySellerRepository,
    )

    return OfferService(SQLAlchemyOfferRepository(session), SQLAlchemySellerRepository(session))


async def get_review_service(session: AsyncSession = Depends(get_session)):
    from src.application.services.review_service import ReviewService
    from src.infrastructure.database.repositories.review_repository_impl import (
        SQLAlchemyReviewRepository,
    )

    return ReviewService(SQLAlchemyReviewRepository(session))


async def get_category_service(session: AsyncSession = Depends(get_session)):
    from src.application.services.category_service import CategoryService
    from src.infrastructure.database.repositories.category_repository_impl import (
        SQLAlchemyCategoryRepository,
    )

    return CategoryService(SQLAlchemyCategoryRepository(session))
