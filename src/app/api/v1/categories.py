from uuid import UUID

from fastapi import APIRouter, Depends

from app.services.category_service import CategoryService
from app.api.deps import get_category_service
from app.domain.schemas.category import (
    CategoryCreateDTO,
    CategoryUpdateDTO,
    CategoryResponseDTO,
)
from app.core.security import require_admin_role

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post(
    "/",
    response_model=CategoryResponseDTO,
    status_code=201,
)
async def create_category(
    dto: CategoryCreateDTO,
    _: object = Depends(require_admin_role),
    service: CategoryService = Depends(get_category_service),
):
    return await service.create_category(dto)


@router.get("/", response_model=list[CategoryResponseDTO])
async def list_categories(
    service: CategoryService = Depends(get_category_service),
):
    return await service.list_categories()


@router.get("/{category_id}", response_model=CategoryResponseDTO)
async def get_category(
    category_id: UUID,
    service: CategoryService = Depends(get_category_service),
):
    return await service.get_category_by_id(category_id)


@router.put("/{category_id}", response_model=CategoryResponseDTO)
async def update_category(
    category_id: UUID,
    dto: CategoryUpdateDTO,
    _: object = Depends(require_admin_role),
    service: CategoryService = Depends(get_category_service),
):
    return await service.update_category(category_id, dto)


@router.delete("/{category_id}", status_code=204)
async def delete_category(
    category_id: UUID,
    _: object = Depends(require_admin_role),
    service: CategoryService = Depends(get_category_service),
):
    await service.delete_category(category_id)
