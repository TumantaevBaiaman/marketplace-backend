from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.domain.exceptions.domain_exceptions import (
    AccessDenied,
    BusinessRuleViolation,
    DomainException,
    EntityAlreadyExists,
    EntityNotFound,
    InvalidValueObject,
)
from src.interfaces.api.errors.domain_handlers import (
    access_denied_handler,
    business_rule_handler,
    domain_exception_handler,
    entity_already_exists_handler,
    entity_not_found_handler,
    invalid_value_object_handler,
)
from src.interfaces.api.errors.http_handlers import (
    http_exception_handler,
    unhandled_exception_handler,
)
from src.interfaces.api.errors.validation_handlers import validation_exception_handler


def register_exception_handlers(app: FastAPI) -> None:
    # Domain (порядок важен: конкретные раньше базового)
    app.add_exception_handler(EntityNotFound, entity_not_found_handler)
    app.add_exception_handler(EntityAlreadyExists, entity_already_exists_handler)
    app.add_exception_handler(InvalidValueObject, invalid_value_object_handler)
    app.add_exception_handler(AccessDenied, access_denied_handler)
    app.add_exception_handler(BusinessRuleViolation, business_rule_handler)
    app.add_exception_handler(DomainException, domain_exception_handler)

    # HTTP
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)

    # Pydantic validation
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    # Fallback
    app.add_exception_handler(Exception, unhandled_exception_handler)
