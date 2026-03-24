from src.application.commands.offer_commands import (
    CreateOfferCommand,
    DeleteOfferCommand,
    UpdateOfferCommand,
)
from src.application.handlers.command_handlers.offer_command_handlers import (
    CreateOfferHandler,
    DeleteOfferHandler,
    UpdateOfferHandler,
)
from src.application.handlers.query_handlers.offer_query_handlers import GetOffersByProductHandler
from src.application.queries.offer_queries import GetOffersByProductQuery
from src.domain.repositories.offer_repository import OfferRepository
from src.domain.repositories.seller_repository import SellerRepository


class OfferService:
    def __init__(self, offer_repo: OfferRepository, seller_repo: SellerRepository | None = None):
        self._create_handler = CreateOfferHandler(offer_repo)
        self._update_handler = UpdateOfferHandler(offer_repo)
        self._delete_handler = DeleteOfferHandler(offer_repo)
        self._get_handler = GetOffersByProductHandler(offer_repo, seller_repo)

    async def create(self, command: CreateOfferCommand):
        return await self._create_handler.handle(command)

    async def update(self, command: UpdateOfferCommand):
        return await self._update_handler.handle(command)

    async def delete(self, command: DeleteOfferCommand):
        return await self._delete_handler.handle(command)

    async def get_by_product(self, query: GetOffersByProductQuery):
        return await self._get_handler.handle(query)
