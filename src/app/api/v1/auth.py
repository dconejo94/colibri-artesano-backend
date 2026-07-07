from fastapi import APIRouter, Depends, Request

from app.api.deps import get_auth_service
from app.config import settings
from app.core.rate_limit import limiter
from app.domain.schemas.auth import (
    AccessTokenResponseDTO,
    LoginDTO,
    RefreshDTO,
    RegisterDTO,
    TokenResponseDTO,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponseDTO, status_code=201)
@limiter.limit(settings.AUTH_RATE_LIMIT)
async def register(
    request: Request,
    dto: RegisterDTO,
    service: AuthService = Depends(get_auth_service),
):
    return await service.register(dto)


@router.post("/login", response_model=TokenResponseDTO)
@limiter.limit(settings.AUTH_RATE_LIMIT)
async def login(
    request: Request,
    dto: LoginDTO,
    service: AuthService = Depends(get_auth_service),
):
    return await service.login(dto)


@router.post("/refresh", response_model=AccessTokenResponseDTO)
@limiter.limit(settings.AUTH_RATE_LIMIT)
async def refresh(
    request: Request,
    dto: RefreshDTO,
    service: AuthService = Depends(get_auth_service),
):
    return await service.refresh(dto)
