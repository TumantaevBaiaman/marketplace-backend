from dataclasses import dataclass


@dataclass
class LoginCommand:
    email: str
    password: str


@dataclass
class AdminLoginCommand:
    email: str
    password: str


@dataclass
class RegisterCommand:
    email: str
    password: str
    first_name: str
    last_name: str


@dataclass
class LogoutCommand:
    jti: str
    ttl_seconds: int
