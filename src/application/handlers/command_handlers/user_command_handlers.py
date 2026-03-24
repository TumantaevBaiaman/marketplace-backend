from src.application.commands.user_commands import CreateUserCommand, DeleteUserCommand
from src.application.dto.user_dto import UserResponseDTO
from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository
from src.domain.value_objects.email import Email


def _to_dto(user: User) -> UserResponseDTO:
    return UserResponseDTO(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        is_active=user.is_active,
        avatar_url=user.avatar_url,
    )


class CreateUserHandler:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    async def handle(self, command: CreateUserCommand) -> UserResponseDTO:
        user = User(email=Email(command.email), name=command.name)
        saved = await self._user_repo.save(user)
        return _to_dto(saved)


class DeleteUserHandler:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    async def handle(self, command: DeleteUserCommand) -> None:
        await self._user_repo.delete(command.user_id)
