import uuid

from src.domain.services.image_service import IImageService
from src.infrastructure.storage.image_service import object_url, upload_product_image


class ImageServiceImpl(IImageService):
    async def upload_product_image(
        self, product_id: uuid.UUID, data: bytes, content_type: str
    ) -> tuple[str, str]:
        return await upload_product_image(product_id, data, content_type)

    def get_object_url(self, path: str | None) -> str | None:
        if path is None:
            return None
        return object_url(path)
