from src.application.commands.user_commands import CreateUserCommand, DeleteUserCommand
from src.application.handlers.command_handlers.user_command_handlers import (
    CreateUserHandler,
    DeleteUserHandler,
)
from src.application.handlers.query_handlers.user_query_handlers import (
    GetUserByEmailHandler,
    GetUserByIdHandler,
)
from src.application.queries.user_queries import GetUserByEmailQuery, GetUserByIdQuery
from src.domain.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, user_repo: UserRepository):
        self._create_handler = CreateUserHandler(user_repo)
        self._delete_handler = DeleteUserHandler(user_repo)
        self._get_by_id_handler = GetUserByIdHandler(user_repo)
        self._get_by_email_handler = GetUserByEmailHandler(user_repo)

    async def create_user(self, command: CreateUserCommand):
        return await self._create_handler.handle(command)

    async def delete_user(self, command: DeleteUserCommand):
        return await self._delete_handler.handle(command)

    async def get_user_by_id(self, query: GetUserByIdQuery):
        return await self._get_by_id_handler.handle(query)

    async def get_user_by_email(self, query: GetUserByEmailQuery):
        return await self._get_by_email_handler.handle(query)
