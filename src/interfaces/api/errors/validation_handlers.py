from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.interfaces.api.errors.schemas import ErrorDetail
from src.interfaces.api.errors.utils import make_error_response


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    details = [
        ErrorDetail(
            field=".".join(str(loc) for loc in err["loc"] if loc != "body"),
            message=err["msg"],
        )
        for err in exc.errors()
    ]
    return make_error_response(
        422, "VALIDATION_ERROR", "Request validation failed", request, details
    )
