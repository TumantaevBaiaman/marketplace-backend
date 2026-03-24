from fastapi import Request
from fastapi.responses import JSONResponse

from src.interfaces.api.errors.schemas import ErrorDetail, ErrorResponse


def make_error_response(
    status_code: int,
    code: str,
    message: str,
    request: Request,
    details: list[ErrorDetail] | None = None,
) -> JSONResponse:
    body = ErrorResponse(
        code=code,
        message=message,
        details=details,
        path=request.url.path,
    )
    return JSONResponse(status_code=status_code, content=body.model_dump(mode="json"))
