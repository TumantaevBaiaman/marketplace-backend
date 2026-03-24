from fastapi import APIRouter

from src.interfaces.api.v1.endpoints.admin_auth import router as admin_auth_router
from src.interfaces.api.v1.endpoints.admin_categories import router as admin_categories_router
from src.interfaces.api.v1.endpoints.admin_offers import router as admin_offers_router
from src.interfaces.api.v1.endpoints.admin_products import router as admin_products_router
from src.interfaces.api.v1.endpoints.admin_sellers import router as admin_sellers_router
from src.interfaces.api.v1.endpoints.auth import router as auth_router
from src.interfaces.api.v1.endpoints.public_products import router as public_products_router
from src.interfaces.api.v1.endpoints.public_sellers import router as public_sellers_router
from src.interfaces.api.v1.endpoints.reviews import router as reviews_router
from src.interfaces.api.v1.endpoints.users import router as users_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(admin_auth_router)
router.include_router(users_router)
router.include_router(public_products_router)
router.include_router(public_sellers_router)
router.include_router(admin_products_router)
router.include_router(admin_sellers_router)
router.include_router(admin_offers_router)
router.include_router(reviews_router)
router.include_router(admin_categories_router)
