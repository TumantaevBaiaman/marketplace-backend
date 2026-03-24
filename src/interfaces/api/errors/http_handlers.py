from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.infrastructure.logging import get_logger
from src.interfaces.api.errors.codes import HTTP_CODES
from src.interfaces.api.errors.utils import make_error_response

logger = get_logger(__name__)


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    code = HTTP_CODES.get(exc.status_code, f"HTTP_{exc.status_code}")
    return make_error_response(exc.status_code, code, str(exc.detail), request)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception: %s", exc)
    return make_error_response(
        500, "INTERNAL_SERVER_ERROR", "An unexpected error occurred", request
    )
