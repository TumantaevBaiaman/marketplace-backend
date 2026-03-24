from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from src.application.commands.auth_commands import LoginCommand, LogoutCommand, RegisterCommand
from src.application.dto.auth_dto import LoginRequest, MeResponse, RegisterRequest, TokenResponse
from src.application.queries.user_queries import GetCurrentUserQuery
from src.application.services.auth_service import AuthService
from src.interfaces.api.v1.dependencies import get_auth_service, get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    token = await service.login(LoginCommand(email=body.email, password=body.password))
    return TokenResponse(access_token=token)


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    body: RegisterRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    await service.register(
        RegisterCommand(
            email=body.email,
            password=body.password,
            first_name=body.first_name,
            last_name=body.last_name,
        )
    )
    token = await service.login(LoginCommand(email=body.email, password=body.password))
    return TokenResponse(access_token=token)


@router.get("/me", response_model=MeResponse)
async def get_me(
    current_user: dict = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> MeResponse:
    user_id = current_user["sub"]
    return await service.get_me(GetCurrentUserQuery(user_id=user_id))


@router.post("/logout", status_code=204)
async def logout(
    current_user: dict = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> None:
    jti = current_user.get("jti")
    exp = current_user.get("exp")
    if jti and exp:
        ttl = int(exp - datetime.now(timezone.utc).timestamp())
        if ttl > 0:
            await service.logout(LogoutCommand(jti=jti, ttl_seconds=ttl))
