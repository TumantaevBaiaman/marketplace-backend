from fastapi import Request
from fastapi.responses import JSONResponse

from src.domain.exceptions.domain_exceptions import (
    AccessDenied,
    BusinessRuleViolation,
    DomainException,
    EntityAlreadyExists,
    EntityNotFound,
    InvalidValueObject,
)
from src.interfaces.api.errors.utils import make_error_response


async def entity_not_found_handler(request: Request, exc: EntityNotFound) -> JSONResponse:
    return make_error_response(404, "NOT_FOUND", exc.message, request)


async def entity_already_exists_handler(request: Request, exc: EntityAlreadyExists) -> JSONResponse:
    return make_error_response(409, "ALREADY_EXISTS", exc.message, request)


async def invalid_value_object_handler(request: Request, exc: InvalidValueObject) -> JSONResponse:
    return make_error_response(400, "INVALID_VALUE", exc.message, request)


async def access_denied_handler(request: Request, exc: AccessDenied) -> JSONResponse:
    return make_error_response(403, "FORBIDDEN", exc.message, request)


async def business_rule_handler(request: Request, exc: BusinessRuleViolation) -> JSONResponse:
    return make_error_response(409, "BUSINESS_RULE_VIOLATION", exc.message, request)


async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    return make_error_response(400, "DOMAIN_ERROR", exc.message, request)
