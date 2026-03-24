import uuid
from abc import ABC, abstractmethod


class IImageService(ABC):
    @abstractmethod
    async def upload_product_image(
        self, product_id: uuid.UUID, data: bytes, content_type: str
    ) -> tuple[str, str]: ...

    @abstractmethod
    def get_object_url(self, path: str | None) -> str | None: ...
