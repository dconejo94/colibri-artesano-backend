from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.services.category_service import CategoryService
from app.api.deps import get_category_service
from app.domain.schemas.category import (
    CategoryCreateDTO,
    CategoryUpdateDTO,
    CategoryResponseDTO,
)
from app.core.exceptions import NotFoundException, ConflictException

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/", response_model=CategoryResponseDTO, status_code=201)
async def create_category(
    dto: CategoryCreateDTO,
    service: CategoryService = Depends(get_category_service),
):
    try:
        return await service.create_category(dto)
    except ConflictException as e:
        raise HTTPException(status_code=409, detail=e.detail)


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
    try:
        return await service.get_category_by_id(category_id)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Category not found")


@router.put("/{category_id}", response_model=CategoryResponseDTO)
async def update_category(
    category_id: UUID,
    dto: CategoryUpdateDTO,
    service: CategoryService = Depends(get_category_service),
):
    try:
        return await service.update_category(category_id, dto)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Category not found")
    except ConflictException as e:
        raise HTTPException(status_code=409, detail=e.detail)


@router.delete("/{category_id}", status_code=204)
async def delete_category(
    category_id: UUID,
    service: CategoryService = Depends(get_category_service),
):
    try:
        await service.delete_category(category_id)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Category not found")
