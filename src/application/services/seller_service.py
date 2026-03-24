from src.application.commands.seller_commands import CreateSellerCommand, UpdateSellerCommand
from src.application.handlers.command_handlers.seller_command_handlers import (
    CreateSellerHandler,
    UpdateSellerHandler,
)
from src.application.handlers.query_handlers.seller_query_handlers import ListSellersHandler
from src.application.queries.seller_queries import ListSellersQuery
from src.domain.repositories.seller_repository import SellerRepository


class SellerService:
    def __init__(self, seller_repo: SellerRepository):
        self._create_handler = CreateSellerHandler(seller_repo)
        self._update_handler = UpdateSellerHandler(seller_repo)
        self._list_handler = ListSellersHandler(seller_repo)
        self._repo = seller_repo

    async def create(self, command: CreateSellerCommand):
        return await self._create_handler.handle(command)

    async def update(self, command: UpdateSellerCommand):
        return await self._update_handler.handle(command)

    async def get_all(self, query: ListSellersQuery):
        return await self._list_handler.handle(query)

    async def get_by_id(self, seller_id):
        return await self._repo.get_by_id(seller_id)
