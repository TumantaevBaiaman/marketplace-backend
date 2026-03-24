import asyncio
import io
import uuid

from PIL import Image

from src.config import get_settings
from src.infrastructure.storage.minio_client import get_minio

_settings = get_settings()
THUMB_SIZE = (300, 300)


def _upload_bytes(data: bytes, key: str, content_type: str) -> None:
    client = get_minio()
    client.put_object(
        bucket_name=_settings.minio.bucket,
        object_name=key,
        data=io.BytesIO(data),
        length=len(data),
        content_type=content_type,
    )


def _make_thumbnail(data: bytes) -> bytes:
    img = Image.open(io.BytesIO(data))
    img.thumbnail(THUMB_SIZE)
    buf = io.BytesIO()
    fmt = img.format or "JPEG"
    img.save(buf, format=fmt)
    return buf.getvalue()


def object_url(key: str) -> str:
    s = _settings.minio
    scheme = "https" if s.secure else "http"
    host = s.public_endpoint or s.endpoint
    return f"{scheme}://{host}/{s.bucket}/{key}"


async def upload_product_image(
    product_id: uuid.UUID, data: bytes, content_type: str
) -> tuple[str, str]:
    """Returns (image_object_key, thumbnail_object_key)."""
    ext = content_type.split("/")[-1]
    image_key = f"products/{product_id}/image.{ext}"
    thumb_key = f"products/{product_id}/thumbnail.{ext}"

    loop = asyncio.get_event_loop()
    thumbnail = await loop.run_in_executor(None, _make_thumbnail, data)

    await loop.run_in_executor(None, _upload_bytes, data, image_key, content_type)
    await loop.run_in_executor(None, _upload_bytes, thumbnail, thumb_key, content_type)

    return image_key, thumb_key
