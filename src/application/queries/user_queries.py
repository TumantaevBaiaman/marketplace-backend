from dataclasses import dataclass


@dataclass
class GetUserByIdQuery:
    user_id: str


@dataclass
class GetUserByEmailQuery:
    email: str


@dataclass
class GetCurrentUserQuery:
    user_id: str
