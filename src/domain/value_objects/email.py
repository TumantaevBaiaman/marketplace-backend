from dataclasses import dataclass

from src.domain.exceptions.domain_exceptions import InvalidValueObject


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        if not self.value or "@" not in self.value:
            raise InvalidValueObject(f"Invalid email: {self.value!r}")
