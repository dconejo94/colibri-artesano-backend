from fastapi import APIRouter, Depends

from app.api.deps import get_user_service
from app.core.security import get_current_user
from app.domain.models.user import User
from app.domain.schemas.user import UserResponseDTO, UserUpdateDTO
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponseDTO)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponseDTO.model_validate(current_user)


@router.put("/me", response_model=UserResponseDTO)
async def update_me(
    body: UserUpdateDTO,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    updated = await service.update_me(current_user, body)
    return UserResponseDTO.model_validate(updated)


@router.delete("/me", status_code=204)
async def delete_me(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    await service.delete_me(current_user)
