import pytest
import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from src.application.handlers.command_handlers.product_command_handlers import (
    CreateProductHandler,
    UpdateProductHandler,
    DeleteProductHandler,
    UploadProductImageHandler,
)
from src.application.commands.product_commands import (
    CreateProductCommand,
    UpdateProductCommand,
    DeleteProductCommand,
    UploadProductImageCommand,
)
from src.application.dto.product_dto import AdminProductResponseDTO
from src.domain.exceptions.domain_exceptions import EntityNotFound
from tests.conftest import make_product


# ── CreateProductHandler ──────────────────────────────────────────────────────

class TestCreateProductHandler:
    def _handler(self, product_repo, attr_repo, audit=None, image_svc=None):
        return CreateProductHandler(product_repo, attr_repo, audit, image_svc)

    @pytest.mark.asyncio
    async def test_creates_product_and_returns_dto(self, mock_product_repo, mock_attr_repo):
        handler = self._handler(mock_product_repo, mock_attr_repo)
        result = await handler.handle(CreateProductCommand(
            name="Laptop",
            price_amount=Decimal("999.99"),
            price_currency="USD",
            stock=5,
        ))

        mock_product_repo.save.assert_called_once()
        assert isinstance(result, AdminProductResponseDTO)
        assert result.name == "Laptop"
        assert result.price.amount == Decimal("999.99")
        assert result.stock == 5

    @pytest.mark.asyncio
    async def test_saves_attributes(self, mock_product_repo, mock_attr_repo):
        handler = self._handler(mock_product_repo, mock_attr_repo)
        await handler.handle(CreateProductCommand(
            name="Phone",
            attributes=[{"key": "color", "value": "black"}, {"key": "size", "value": "6.1"}],
        ))

        assert mock_attr_repo.save.call_count == 2

    @pytest.mark.asyncio
    async def test_resolves_image_url_when_image_service_provided(
        self, mock_product_repo, mock_attr_repo, mock_image_service
    ):
        from src.domain.entities.product import Product
        product_with_image = make_product()
        product_with_image.image_object_key = "products/img.jpg"

        original_save = mock_product_repo.save

        async def save_and_set_key(product):
            product.image_object_key = "products/img.jpg"

        mock_product_repo.save = save_and_set_key
        mock_image_service.get_object_url = MagicMock(return_value="https://cdn.example.com/img.jpg")

        handler = self._handler(mock_product_repo, mock_attr_repo, image_svc=mock_image_service)
        result = await handler.handle(CreateProductCommand(name="Test"))

        assert result.image_url == "https://cdn.example.com/img.jpg"

    @pytest.mark.asyncio
    async def test_no_image_url_when_no_image_service(self, mock_product_repo, mock_attr_repo):
        handler = self._handler(mock_product_repo, mock_attr_repo, image_svc=None)
        result = await handler.handle(CreateProductCommand(name="Test"))

        assert result.image_url is None
        assert result.thumbnail_url is None


# ── UpdateProductHandler ──────────────────────────────────────────────────────

class TestUpdateProductHandler:
    def _handler(self, product_repo, attr_repo, audit=None, image_svc=None):
        return UpdateProductHandler(product_repo, attr_repo, audit, image_svc)

    @pytest.mark.asyncio
    async def test_updates_product_fields(self, mock_product_repo, mock_attr_repo):
        product = make_product(name="Old Name")
        mock_product_repo.get_by_id = AsyncMock(return_value=product)

        handler = self._handler(mock_product_repo, mock_attr_repo)
        result = await handler.handle(UpdateProductCommand(
            product_id=product.id,
            name="New Name",
            stock=20,
        ))

        assert result.name == "New Name"
        assert result.stock == 20
        mock_product_repo.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_when_product_not_found(self, mock_product_repo, mock_attr_repo):
        mock_product_repo.get_by_id = AsyncMock(return_value=None)

        handler = self._handler(mock_product_repo, mock_attr_repo)
        with pytest.raises(EntityNotFound):
            await handler.handle(UpdateProductCommand(product_id=uuid.uuid4(), name="X"))

    @pytest.mark.asyncio
    async def test_partial_update_leaves_other_fields(self, mock_product_repo, mock_attr_repo):
        product = make_product(name="Original", stock=99)
        mock_product_repo.get_by_id = AsyncMock(return_value=product)

        handler = self._handler(mock_product_repo, mock_attr_repo)
        result = await handler.handle(UpdateProductCommand(
            product_id=product.id,
            name="Updated",
        ))

        assert result.name == "Updated"
        assert result.stock == 99

    @pytest.mark.asyncio
    async def test_replaces_attributes_when_provided(self, mock_product_repo, mock_attr_repo):
        product = make_product()
        mock_product_repo.get_by_id = AsyncMock(return_value=product)
        mock_attr_repo.get_by_product = AsyncMock(return_value=[])

        handler = self._handler(mock_product_repo, mock_attr_repo)
        await handler.handle(UpdateProductCommand(
            product_id=product.id,
            attributes=[{"key": "color", "value": "red"}],
        ))

        mock_attr_repo.delete_by_product.assert_called_once_with(product.id)
        mock_attr_repo.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_does_not_touch_attributes_when_not_provided(
        self, mock_product_repo, mock_attr_repo
    ):
        product = make_product()
        mock_product_repo.get_by_id = AsyncMock(return_value=product)

        handler = self._handler(mock_product_repo, mock_attr_repo)
        await handler.handle(UpdateProductCommand(product_id=product.id, name="X"))

        mock_attr_repo.delete_by_product.assert_not_called()


# ── DeleteProductHandler ──────────────────────────────────────────────────────

class TestDeleteProductHandler:
    def _handler(self, product_repo, audit=None):
        return DeleteProductHandler(product_repo, audit)

    @pytest.mark.asyncio
    async def test_deletes_product(self, mock_product_repo):
        product = make_product()
        mock_product_repo.get_by_id = AsyncMock(return_value=product)

        handler = self._handler(mock_product_repo)
        await handler.handle(DeleteProductCommand(product_id=product.id))

        mock_product_repo.delete.assert_called_once_with(product.id)

    @pytest.mark.asyncio
    async def test_raises_when_product_not_found(self, mock_product_repo):
        mock_product_repo.get_by_id = AsyncMock(return_value=None)

        handler = self._handler(mock_product_repo)
        with pytest.raises(EntityNotFound):
            await handler.handle(DeleteProductCommand(product_id=uuid.uuid4()))

    @pytest.mark.asyncio
    async def test_returns_none(self, mock_product_repo):
        product = make_product()
        mock_product_repo.get_by_id = AsyncMock(return_value=product)

        handler = self._handler(mock_product_repo)
        result = await handler.handle(DeleteProductCommand(product_id=product.id))

        assert result is None


# ── UploadProductImageHandler ─────────────────────────────────────────────────

class TestUploadProductImageHandler:
    @pytest.mark.asyncio
    async def test_uploads_image_and_returns_urls(
        self, mock_product_repo, mock_image_service
    ):
        product = make_product()
        mock_product_repo.get_by_id = AsyncMock(return_value=product)
        mock_image_service.upload_product_image = AsyncMock(
            return_value=("img/key.jpg", "thumb/key.jpg")
        )
        mock_image_service.get_object_url = MagicMock(
            side_effect=lambda k: f"https://cdn.example.com/{k}"
        )

        handler = UploadProductImageHandler(mock_product_repo, mock_image_service)
        result = await handler.handle(UploadProductImageCommand(
            product_id=product.id,
            data=b"image_bytes",
            content_type="image/jpeg",
        ))

        assert result["image_url"] == "https://cdn.example.com/img/key.jpg"
        assert result["thumbnail_url"] == "https://cdn.example.com/thumb/key.jpg"
        assert product.image_object_key == "img/key.jpg"
        assert product.thumbnail_object_key == "thumb/key.jpg"
        mock_product_repo.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_when_product_not_found(
        self, mock_product_repo, mock_image_service
    ):
        mock_product_repo.get_by_id = AsyncMock(return_value=None)

        handler = UploadProductImageHandler(mock_product_repo, mock_image_service)
        with pytest.raises(EntityNotFound):
            await handler.handle(UploadProductImageCommand(
                product_id=uuid.uuid4(),
                data=b"bytes",
                content_type="image/jpeg",
            ))
