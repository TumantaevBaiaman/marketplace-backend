import asyncio

from minio import Minio

from src.config import get_settings

_settings = get_settings()

minio_client: Minio | None = None


def get_minio() -> Minio:
    return minio_client


async def init_minio() -> None:
    global minio_client
    minio_client = Minio(
        endpoint=_settings.minio.endpoint,
        access_key=_settings.minio.access_key,
        secret_key=_settings.minio.secret_key,
        secure=_settings.minio.secure,
    )
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _ensure_bucket)


def _ensure_bucket() -> None:
    import json

    bucket = _settings.minio.bucket
    if not minio_client.bucket_exists(bucket):
        minio_client.make_bucket(bucket)
    policy = json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": ["*"]},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{bucket}/*"],
                }
            ],
        }
    )
    minio_client.set_bucket_policy(bucket, policy)


async def close_minio() -> None:
    pass
