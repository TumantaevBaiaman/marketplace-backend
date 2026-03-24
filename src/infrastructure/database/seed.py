"""
Seed script — 100 products, 5 sellers, 2-10 offers, reviews.
Images downloaded concurrently from picsum.photos → MinIO.
Run: docker exec marketplace-stack-backend-1 python3 -m src.infrastructure.database.seed
"""

import asyncio
import io
import random
import uuid
from datetime import date, timedelta
from decimal import Decimal
from urllib.request import urlopen

from minio import Minio
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import src.infrastructure.database.models  # noqa: F401 — registers all ORM mappers
from src.config import get_settings
from src.domain.enums.offer_condition import OfferCondition
from src.domain.enums.user_role import UserRole
from src.domain.enums.user_status import UserStatus
from src.infrastructure.database.models.category_model import CategoryModel
from src.infrastructure.database.models.offer_model import OfferModel
from src.infrastructure.database.models.product_attribute_model import ProductAttributeModel
from src.infrastructure.database.models.product_model import ProductModel
from src.infrastructure.database.models.review_model import ReviewModel
from src.infrastructure.database.models.seller_model import SellerModel
from src.infrastructure.database.models.user_model import UserModel
from src.infrastructure.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)
settings = get_settings()

PRODUCT_NAMES = [
    "Wireless Headphones",
    "Smart Watch",
    "Bluetooth Speaker",
    "Laptop Stand",
    "Mechanical Keyboard",
    "Gaming Mouse",
    "USB-C Hub",
    "Webcam HD",
    "LED Desk Lamp",
    "Phone Case",
    "Screen Protector",
    "Portable Charger",
    "Noise Cancelling Earbuds",
    "Smart Home Hub",
    "Fitness Tracker",
    "Action Camera",
    "Drone Mini",
    "VR Headset",
    "E-reader",
    "Tablet Stand",
    "Power Bank",
    "Wireless Charger",
    "SSD Drive",
    "RAM Module",
    "CPU Cooler",
]

PRODUCT_DESCRIPTIONS = [
    "High-quality product with premium build and exceptional performance.",
    "Designed for everyday use with a focus on durability and comfort.",
    "Feature-packed device offering great value for money.",
    "Next-generation technology for a seamless user experience.",
    "Compact and lightweight, perfect for on-the-go use.",
]

SELLER_COUNTRIES = ["US", "DE", "CN", "GB", "KZ", "RU", "AE"]

ATTRIBUTES = {
    "Color": ["Black", "White", "Silver", "Gold", "Blue", "Red"],
    "Memory": ["64GB", "128GB", "256GB", "512GB"],
    "Battery": ["2000mAh", "4000mAh", "6000mAh", "10000mAh"],
    "Connectivity": ["Bluetooth 5.0", "Wi-Fi 6", "USB-C", "Lightning"],
    "Weight": ["100g", "200g", "350g", "500g", "1kg"],
    "Warranty": ["1 year", "2 years", "3 years"],
    "Material": ["Plastic", "Aluminum", "Carbon Fiber", "Leather"],
    "Resolution": ["720p", "1080p", "4K", "8K"],
}

SELLER_NAMES = ["TechZone LLC", "BestGadgets", "ElectroHub", "SmartShop", "GigaStore"]

REVIEW_AUTHORS = [
    "Алексей К.",
    "Мария С.",
    "Ivan P.",
    "Анна Л.",
    "Dmitry V.",
    "Ольга М.",
    "Сергей Р.",
    "Elena T.",
    "Николай Б.",
    "Kate W.",
]

REVIEW_TEXTS = [
    "Отличный товар, рекомендую!",
    "Качество на высоте, быстрая доставка.",
    "Всё пришло в срок, упаковка целая.",
    "Неплохо за эти деньги.",
    "Уже второй раз беру — доволен.",
    "Хорошее соотношение цена/качество.",
    "Доставили быстро, товар соответствует описанию.",
    "Немного разочарован качеством, но в целом норм.",
    "Превзошёл ожидания!",
    "Буду брать ещё.",
]

THUMB_SIZE = (300, 300)


def current_week_date() -> date:
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    start = max(today, monday)
    return start + timedelta(days=random.randint(0, max((sunday - start).days, 0)))


# ── MinIO ────────────────────────────────────────────────────────────────────


def _make_minio() -> Minio:
    return Minio(
        endpoint=settings.minio.endpoint,
        access_key=settings.minio.access_key,
        secret_key=settings.minio.secret_key,
        secure=settings.minio.secure,
    )


def _download_and_upload(index: int, product_id: uuid.UUID) -> tuple[str, str] | tuple[None, None]:
    """Скачивает фото и загружает в MinIO. Блокирующая — запускается в executor."""
    try:
        url = f"https://picsum.photos/seed/{index}/640/640"
        with urlopen(url, timeout=15) as resp:
            data = resp.read()

        img = Image.open(io.BytesIO(data)).convert("RGB")
        img.thumbnail(THUMB_SIZE)
        thumb_buf = io.BytesIO()
        img.save(thumb_buf, format="JPEG")
        thumb_data = thumb_buf.getvalue()

        client = _make_minio()
        bucket = settings.minio.bucket
        image_key = f"products/{product_id}/image.jpg"
        thumb_key = f"products/{product_id}/thumbnail.jpg"

        client.put_object(bucket, image_key, io.BytesIO(data), len(data), "image/jpeg")
        client.put_object(bucket, thumb_key, io.BytesIO(thumb_data), len(thumb_data), "image/jpeg")

        return image_key, thumb_key
    except Exception as exc:
        logger.warning("Image failed for index %d: %s", index, exc)
        return None, None


async def upload_all_images(product_ids: list[uuid.UUID]) -> list[tuple]:
    """Загружает все 100 картинок параллельно (макс. 15 одновременно)."""
    sem = asyncio.Semaphore(15)
    loop = asyncio.get_event_loop()

    async def one(i: int, pid: uuid.UUID):
        async with sem:
            return await loop.run_in_executor(None, _download_and_upload, i + 1, pid)

    results = await asyncio.gather(*[one(i, pid) for i, pid in enumerate(product_ids)])
    return results


# ── Seed ─────────────────────────────────────────────────────────────────────


async def seed(session: AsyncSession) -> None:
    # Загружаем категории из БД (созданы миграцией 0007)
    from sqlalchemy import select as sa_select

    result = await session.execute(
        sa_select(CategoryModel).where(CategoryModel.parent_id.isnot(None))
    )
    leaf_categories = result.scalars().all()
    if not leaf_categories:
        raise RuntimeError("Категории не найдены. Запустите: alembic upgrade head")
    logger.info("Loaded %d leaf categories from DB", len(leaf_categories))

    # Sellers
    logger.info("Creating sellers...")
    sellers = []
    for i, name in enumerate(SELLER_NAMES):
        s = SellerModel(
            id=uuid.uuid4(),
            name=name,
            description=f"Official store of {name}. Fast shipping and quality guarantee.",
            email=f"contact@{name.lower().replace(' ', '')}.com",
            phone=f"+1-800-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            website=f"https://www.{name.lower().replace(' ', '')}.com",
            country=random.choice(SELLER_COUNTRIES),
            rating=Decimal(str(round(random.uniform(3.5, 5.0), 2))),
            review_count=random.randint(10, 500),
            is_verified=random.choice([True, False]),
        )
        session.add(s)
        sellers.append(s)
    await session.commit()

    # Create reviewer users pool
    reviewer_ids: list[uuid.UUID] = []
    for idx, author in enumerate(REVIEW_AUTHORS * 2):  # 20 users
        u = UserModel(
            id=uuid.uuid4(),
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            first_name=author.split()[0],
            last_name=author.split()[-1] if len(author.split()) > 1 else "User",
        )
        session.add(u)
        reviewer_ids.append(u.id)
    await session.commit()

    # Pre-generate product IDs
    product_ids = [uuid.uuid4() for _ in range(100)]

    # Download + upload all images concurrently
    logger.info("Downloading & uploading 100 images in parallel...")
    image_keys = await upload_all_images(product_ids)
    logger.info("Images done.")

    # Insert products, attributes, offers, reviews
    logger.info("Inserting products...")
    for i, product_id in enumerate(product_ids):
        image_key, thumb_key = image_keys[i]

        product = ProductModel(
            id=product_id,
            name=f"{random.choice(PRODUCT_NAMES)} {i + 1}",
            description=random.choice(PRODUCT_DESCRIPTIONS),
            category_id=random.choice(leaf_categories).id,
            sku=f"SKU-{i + 1:04d}",
            price_amount=Decimal(str(round(random.uniform(9.99, 1999.99), 2))),
            price_currency=random.choice(["USD", "EUR", "RUB", "KZT"]),
            stock=random.randint(0, 200),
            is_active=True,
            views_count=random.randint(0, 5000),
            image_object_key=image_key,
            thumbnail_object_key=thumb_key,
        )
        session.add(product)
        await session.flush()

        # 2–6 attributes
        for key in random.sample(list(ATTRIBUTES), k=random.randint(2, 6)):
            session.add(
                ProductAttributeModel(
                    id=uuid.uuid4(),
                    product_id=product_id,
                    key=key,
                    value=random.choice(ATTRIBUTES[key]),
                )
            )

        # 2–10 offers
        for seller in random.sample(sellers, k=random.randint(2, min(5, len(sellers)))):
            for _ in range(random.randint(1, 2)):
                days_min = random.randint(1, 5)
                days_max = days_min + random.randint(1, 5)
                session.add(
                    OfferModel(
                        id=uuid.uuid4(),
                        product_id=product_id,
                        seller_id=seller.id,
                        price_amount=Decimal(str(round(random.uniform(9.99, 999.99), 2))),
                        price_currency="USD",
                        condition=random.choice(list(OfferCondition)),
                        quantity=random.randint(1, 50),
                        is_available=random.choice([True, True, True, False]),
                        delivery_date=current_week_date(),
                        delivery_days_min=days_min,
                        delivery_days_max=days_max,
                    )
                )

        # 2–8 reviews (уникальный user_id на каждый отзыв в рамках товара)
        sampled_reviewers = random.sample(
            reviewer_ids, k=random.randint(2, min(8, len(reviewer_ids)))
        )
        for reviewer_id in sampled_reviewers:
            session.add(
                ReviewModel(
                    id=uuid.uuid4(),
                    product_id=product_id,
                    user_id=reviewer_id,
                    author=random.choice(REVIEW_AUTHORS),
                    rating=random.randint(1, 5),
                    text=random.choice(REVIEW_TEXTS),
                    is_verified_purchase=random.choice([True, False]),
                    helpful_count=random.randint(0, 50),
                )
            )

        if (i + 1) % 10 == 0:
            await session.commit()
            logger.info("Products: %d/100", i + 1)

    await session.commit()
    logger.info("Seed complete!")


async def main() -> None:
    engine = create_async_engine(settings.db.url, echo=False)
    maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with maker() as session:
        await seed(session)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
