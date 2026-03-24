from src.application.commands.product_commands import (
    CreateProductCommand,
    DeleteProductCommand,
    UpdateProductCommand,
    UploadProductImageCommand,
)
from src.application.handlers.command_handlers.audit_command_handlers import (
    WriteProductAuditLogHandler,
)
from src.application.handlers.command_handlers.product_command_handlers import (
    CreateProductHandler,
    DeleteProductHandler,
    UpdateProductHandler,
    UploadProductImageHandler,
)
from src.application.handlers.query_handlers.audit_query_handlers import GetProductAuditLogHandler
from src.application.handlers.query_handlers.product_query_handlers import (
    AdminGetProductHandler,
    AdminListProductsHandler,
    GetPublicProductDetailsHandler,
    ListPublicProductsHandler,
)
from src.application.queries.audit_queries import GetProductAuditLogQuery
from src.application.queries.product_queries import (
    AdminGetProductQuery,
    AdminListProductsQuery,
    GetPublicProductDetailsQuery,
    ListPublicProductsQuery,
)
from src.domain.repositories.offer_repository import OfferRepository
from src.domain.repositories.product_attribute_repository import ProductAttributeRepository
from src.domain.repositories.product_audit_log_repository import ProductAuditLogRepository
from src.domain.repositories.product_repository import ProductRepository
from src.domain.repositories.seller_repository import SellerRepository
from src.domain.services.image_service import IImageService


class ProductService:
    def __init__(
        self,
        product_repo: ProductRepository,
        attr_repo: ProductAttributeRepository,
        offer_repo: OfferRepository,
        seller_repo: SellerRepository,
        audit_log_repo: ProductAuditLogRepository | None = None,
        image_service: IImageService | None = None,
    ):
        audit_handler = WriteProductAuditLogHandler(audit_log_repo) if audit_log_repo else None

        # Command handlers
        self._create_handler = CreateProductHandler(
            product_repo, attr_repo, audit_handler, image_service
        )
        self._update_handler = UpdateProductHandler(
            product_repo, attr_repo, audit_handler, image_service
        )
        self._delete_handler = DeleteProductHandler(product_repo, audit_handler)
        self._upload_image_handler = (
            UploadProductImageHandler(product_repo, image_service) if image_service else None
        )

        self._product_repo = product_repo

        # Query handlers
        self._list_public_handler = ListPublicProductsHandler(
            product_repo, offer_repo, image_service
        )
        self._get_details_handler = GetPublicProductDetailsHandler(
            product_repo, attr_repo, offer_repo, seller_repo, image_service
        )
        self._admin_list_handler = AdminListProductsHandler(product_repo, attr_repo, image_service)
        self._admin_get_handler = AdminGetProductHandler(product_repo, attr_repo, image_service)
        self._audit_log_handler = (
            GetProductAuditLogHandler(audit_log_repo) if audit_log_repo else None
        )

    # ── Commands ──────────────────────────────────────────────────────────────

    async def admin_create(self, command: CreateProductCommand):
        return await self._create_handler.handle(command)

    async def admin_update(self, command: UpdateProductCommand):
        return await self._update_handler.handle(command)

    async def admin_delete(self, command: DeleteProductCommand) -> None:
        await self._delete_handler.handle(command)

    async def admin_upload_image(self, command: UploadProductImageCommand) -> dict:
        if not self._upload_image_handler:
            raise RuntimeError("Image service is not configured")
        return await self._upload_image_handler.handle(command)

    # ── Queries ───────────────────────────────────────────────────────────────

    async def list_public(self, query: ListPublicProductsQuery):
        return await self._list_public_handler.handle(query)

    async def get_public_details(self, query: GetPublicProductDetailsQuery):
        return await self._get_details_handler.handle(query)

    async def admin_list(self, query: AdminListProductsQuery):
        return await self._admin_list_handler.handle(query)

    async def admin_count(self) -> int:
        return await self._product_repo.count()

    async def admin_get(self, query: AdminGetProductQuery):
        return await self._admin_get_handler.handle(query)

    async def get_audit_log(self, query: GetProductAuditLogQuery):
        if not self._audit_log_handler:
            return None
        return await self._audit_log_handler.handle(query)
