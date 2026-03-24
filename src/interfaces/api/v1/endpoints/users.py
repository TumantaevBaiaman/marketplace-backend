import uuid

from fastapi import APIRouter, Depends

from src.application.commands.user_commands import CreateUserCommand, DeleteUserCommand
from src.application.dto.user_dto import CreateUserDTO, UserResponseDTO
from src.application.queries.user_queries import GetUserByIdQuery
from src.application.services.user_service import UserService
from src.interfaces.api.v1.dependencies import get_user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponseDTO)
async def create_user(dto: CreateUserDTO, service: UserService = Depends(get_user_service)):
    return await service.create_user(
        CreateUserCommand(email=dto.email, name=dto.name, password=dto.password)
    )


@router.get("/{user_id}", response_model=UserResponseDTO)
async def get_user(user_id: uuid.UUID, service: UserService = Depends(get_user_service)):
    return await service.get_user_by_id(GetUserByIdQuery(user_id=str(user_id)))


@router.delete("/{user_id}")
async def delete_user(user_id: uuid.UUID, service: UserService = Depends(get_user_service)):
    await service.delete_user(DeleteUserCommand(user_id=str(user_id)))
    return {"ok": True}
