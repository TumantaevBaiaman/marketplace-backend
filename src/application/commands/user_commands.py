from dataclasses import dataclass


@dataclass
class CreateUserCommand:
    email: str
    name: str
    password: str


@dataclass
class DeleteUserCommand:
    user_id: str
