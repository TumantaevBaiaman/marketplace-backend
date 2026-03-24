from src.application.commands.audit_commands import WriteProductAuditLogCommand
from src.application.commands.product_commands import (
    CreateProductCommand,
    DeleteProductCommand,
    UpdateProductCommand,
    UploadProductImageCommand,
)
from src.application.dto.product_dto import AdminProductResponseDTO, MoneyDTO, ProductAttributeDTO
from src.application.handlers.command_handlers.audit_command_handlers import (
    WriteProductAuditLogHandler,
)
from src.domain.entities.product import Product
from src.domain.entities.product_attribute import ProductAttribute
from src.domain.exceptions.domain_exceptions import EntityNotFound
from src.domain.repositories.product_attribute_repository import ProductAttributeRepository
from src.domain.repositories.product_repository import ProductRepository
from src.domain.services.image_service import IImageService

_TRACKED = (
    "name",
    "description",
    "sku",
    "category_id",
    "price_amount",
    "price_currency",
    "stock",
    "is_active",
)


def _snapshot(product: Product) -> dict:
    return {
        f: str(getattr(product, f)) if getattr(product, f) is not None else None for f in _TRACKED
    }


def _compute_diff(before: dict, after: dict) -> dict:
    return {
        k: {"before": before.get(k), "after": after.get(k)}
        for k in _TRACKED
        if before.get(k) != after.get(k)
    }


def _create_diff(after: dict) -> dict:
    return {k: {"before": None, "after": after.get(k)} for k in _TRACKED}


def _delete_diff(before: dict) -> dict:
    return {k: {"before": before.get(k), "after": None} for k in _TRACKED}


class CreateProductHandler:
    def __init__(
        self,
        product_repo: ProductRepository,
        attr_repo: ProductAttributeRepository,
        audit_handler: WriteProductAuditLogHandler | None = None,
        image_service: IImageService | None = None,
    ):
        self._products = product_repo
        self._attrs = attr_repo
        self._audit = audit_handler
        self._image_service = image_service

    async def handle(self, command: CreateProductCommand) -> AdminProductResponseDTO:
        product = Product(
            name=command.name,
            description=command.description,
            sku=command.sku,
            category_id=command.category_id,
            price_amount=command.price_amount,
            price_currency=command.price_currency,
            stock=command.stock,
        )
        await self._products.save(product)
        saved_attrs = []
        for a in command.attributes:
            attr = ProductAttribute(product_id=product.id, key=a["key"], value=a["value"])
            await self._attrs.save(attr)
            saved_attrs.append(attr)

        if self._audit:
            await self._audit.handle(
                WriteProductAuditLogCommand(
                    product_id=product.id,
                    action="create",
                    diff=_create_diff(_snapshot(product)),
                    actor_id=command.actor_id,
                    actor_email=command.actor_email,
                )
            )

        image_url = None
        thumbnail_url = None
        if self._image_service:
            if product.image_object_key:
                image_url = self._image_service.get_object_url(product.image_object_key)
            if product.thumbnail_object_key:
                thumbnail_url = self._image_service.get_object_url(product.thumbnail_object_key)

        return AdminProductResponseDTO(
            id=product.id,
            name=product.name,
            description=product.description,
            sku=product.sku,
            category_id=product.category_id,
            price=MoneyDTO(amount=product.price_amount, currency=product.price_currency),
            stock=product.stock,
            is_active=product.is_active,
            image_url=image_url,
            thumbnail_url=thumbnail_url,
            attributes=[ProductAttributeDTO(key=a.key, value=a.value) for a in saved_attrs],
        )


class UpdateProductHandler:
    def __init__(
        self,
        product_repo: ProductRepository,
        attr_repo: ProductAttributeRepository,
        audit_handler: WriteProductAuditLogHandler | None = None,
        image_service: IImageService | None = None,
    ):
        self._products = product_repo
        self._attrs = attr_repo
        self._audit = audit_handler
        self._image_service = image_service

    async def handle(self, command: UpdateProductCommand) -> AdminProductResponseDTO:
        product = await self._products.get_by_id(command.product_id)
        if not product:
            raise EntityNotFound("Product not found")

        before = _snapshot(product)

        if command.name is not None:
            product.name = command.name
        if command.description is not None:
            product.description = command.description
        if command.sku is not None:
            product.sku = command.sku
        if command.category_id is not None:
            product.category_id = command.category_id
        if command.price_amount is not None:
            product.price_amount = command.price_amount
        if command.price_currency is not None:
            product.price_currency = command.price_currency
        if command.stock is not None:
            product.stock = command.stock
        if command.is_active is not None:
            product.is_active = command.is_active
        await self._products.save(product)

        if command.attributes is not None:
            await self._attrs.delete_by_product(command.product_id)
            for a in command.attributes:
                await self._attrs.save(
                    ProductAttribute(product_id=command.product_id, key=a["key"], value=a["value"])
                )

        after = _snapshot(product)
        diff = _compute_diff(before, after)

        if self._audit and diff:
            await self._audit.handle(
                WriteProductAuditLogCommand(
                    product_id=product.id,
                    action="update",
                    diff=diff,
                    actor_id=command.actor_id,
                    actor_email=command.actor_email,
                )
            )

        attrs = await self._attrs.get_by_product(command.product_id)

        image_url = None
        thumbnail_url = None
        if self._image_service:
            if product.image_object_key:
                image_url = self._image_service.get_object_url(product.image_object_key)
            if product.thumbnail_object_key:
                thumbnail_url = self._image_service.get_object_url(product.thumbnail_object_key)

        return AdminProductResponseDTO(
            id=product.id,
            name=product.name,
            description=product.description,
            sku=product.sku,
            category_id=product.category_id,
            price=MoneyDTO(amount=product.price_amount, currency=product.price_currency),
            stock=product.stock,
            is_active=product.is_active,
            image_url=image_url,
            thumbnail_url=thumbnail_url,
            attributes=[ProductAttributeDTO(key=a.key, value=a.value) for a in attrs],
        )


class DeleteProductHandler:
    def __init__(
        self,
        product_repo: ProductRepository,
        audit_handler: WriteProductAuditLogHandler | None = None,
    ):
        self._products = product_repo
        self._audit = audit_handler

    async def handle(self, command: DeleteProductCommand) -> None:
        product = await self._products.get_by_id(command.product_id)
        if not product:
            raise EntityNotFound("Product not found")

        if self._audit:
            await self._audit.handle(
                WriteProductAuditLogCommand(
                    product_id=product.id,
                    action="delete",
                    diff=_delete_diff(_snapshot(product)),
                    actor_id=command.actor_id,
                    actor_email=command.actor_email,
                )
            )

        await self._products.delete(command.product_id)


class UploadProductImageHandler:
    def __init__(self, product_repo: ProductRepository, image_service: IImageService):
        self._products = product_repo
        self._image_service = image_service

    async def handle(self, command: UploadProductImageCommand) -> dict:
        product = await self._products.get_by_id(command.product_id)
        if not product:
            raise EntityNotFound("Product not found")
        image_key, thumb_key = await self._image_service.upload_product_image(
            command.product_id, command.data, command.content_type
        )
        product.image_object_key = image_key
        product.thumbnail_object_key = thumb_key
        await self._products.save(product)
        return {
            "image_url": self._image_service.get_object_url(image_key),
            "thumbnail_url": self._image_service.get_object_url(thumb_key),
        }
