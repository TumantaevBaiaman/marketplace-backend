from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from src.config import get_settings
from src.interfaces.api.v1.router import router as v1_router
from src.interfaces.api.errors.registry import register_exception_handlers
from src.infrastructure.cache.cache import init_redis, close_redis
from src.infrastructure.database.base import init_db, close_db
from src.infrastructure.storage.minio_client import init_minio, close_minio
from src.infrastructure.logging import configure_logging, get_logger
import src.infrastructure.database.models  # noqa: F401 — registers all ORM mappers

configure_logging()
logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)
    await init_db()
    await init_redis()
    await init_minio()
    logger.info("All services initialized")
    yield
    logger.info("Shutting down...")
    await close_minio()
    await close_redis()
    await close_db()
    logger.info("Shutdown complete")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=settings.allowed_methods,
    allow_headers=settings.allowed_headers,
    allow_credentials=True,
)

register_exception_handlers(app)

app.include_router(v1_router, prefix=f"{settings.api_prefix}/v1")

Instrumentator().instrument(app).expose(app, include_in_schema=False)


@app.get("/health", tags=["healthcheck"])
async def health():
    return {"status": "ok"}
