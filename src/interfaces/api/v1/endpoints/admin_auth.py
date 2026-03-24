from fastapi import APIRouter, Depends

from src.application.commands.auth_commands import AdminLoginCommand
from src.application.dto.auth_dto import LoginRequest, TokenResponse
from src.application.services.auth_service import AuthService
from src.interfaces.api.v1.dependencies import get_auth_service

router = APIRouter(prefix="/admin/auth", tags=["AdminAuth"])


@router.post("/login", response_model=TokenResponse)
async def admin_login(
    body: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    token = await service.admin_login(AdminLoginCommand(email=body.email, password=body.password))
    return TokenResponse(access_token=token)
