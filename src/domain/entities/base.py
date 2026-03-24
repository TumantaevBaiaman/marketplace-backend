import uuid
from dataclasses import dataclass, field


@dataclass
class BaseEntity:
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseEntity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
