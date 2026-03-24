from datetime import datetime, timezone

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Single validation error detail."""

    field: str
    message: str


class ErrorResponse(BaseModel):
    """Unified error response — единственный формат ошибок во всём API."""

    code: str = Field(description="Machine-readable error code")
    message: str = Field(description="Human-readable message")
    details: list[ErrorDetail] | None = Field(default=None, description="Validation field errors")
    path: str = Field(description="Request path")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "code": "NOT_FOUND",
                    "message": "User not found",
                    "details": None,
                    "path": "/api/v1/users/123",
                    "timestamp": "2024-01-01T00:00:00Z",
                },
                {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": [
                        {"field": "email", "message": "value is not a valid email address"}
                    ],
                    "path": "/api/v1/users",
                    "timestamp": "2024-01-01T00:00:00Z",
                },
            ]
        }
    }
