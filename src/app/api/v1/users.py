from fastapi import APIRouter, Depends, Query

from app.api.deps import get_user_service, get_product_service, get_store_service
from app.core.security import get_current_user
from app.domain.models.user import User
from app.domain.schemas.user import UserResponseDTO, UserUpdateDTO
from app.domain.schemas.paginated_response import PaginatedResponse
from app.domain.schemas.product import ProductListDTO
from app.domain.schemas.store import StoreResponseDTO
from app.services.user_service import UserService
from app.services.product_service import ProductService
from app.services.store_service import StoreService

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



@router.get("/me/favorites/products", response_model=PaginatedResponse[ProductListDTO])
async def list_favorite_products(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: ProductService = Depends(get_product_service),
):
    return await service.list_favorite_products(current_user.id, page, limit)



@router.get("/me/followed_stores", response_model=PaginatedResponse[StoreResponseDTO])
async def list_followed_stores(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: StoreService = Depends(get_store_service),
):
    return await service.list_followed_stores(current_user.id, page, limit)
