class DomainException(Exception):
    """Base domain exception."""

    message: str = "Domain error"

    def __init__(self, message: str | None = None):
        self.message = message or self.__class__.message
        super().__init__(self.message)


class EntityNotFound(DomainException):
    message = "Entity not found"


class EntityAlreadyExists(DomainException):
    message = "Entity already exists"


class InvalidValueObject(DomainException):
    message = "Invalid value"


class AccessDenied(DomainException):
    message = "Access denied"


class BusinessRuleViolation(DomainException):
    message = "Business rule violation"
