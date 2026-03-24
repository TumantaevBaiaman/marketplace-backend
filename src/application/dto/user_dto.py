import uuid

from pydantic import BaseModel, EmailStr


class CreateUserDTO(BaseModel):
    email: EmailStr
    name: str
    password: str


class UserResponseDTO(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    role: str
    is_active: bool
    avatar_url: str | None = None
