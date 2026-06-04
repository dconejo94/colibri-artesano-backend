from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException

from app.services.store_service import StoreService
from app.services.product_service import ProductService
from app.services.order_service import OrderService
from app.api.deps import get_store_service, get_product_service, get_order_service
from app.domain.schemas.store import (
    StoreCreateDTO,
    StoreUpdateDTO,
    StoreResponseDTO,
)
from app.domain.schemas.paginated_response import PaginatedResponse
from app.domain.schemas.product import ProductCreateDTO, ProductResponseDTO
from app.domain.schemas.order import StoreOrderResponseDTO, StoreOrderStatusUpdateDTO
from app.core.exceptions import NotFoundException, ConflictException
from app.core.security import require_vendor_role

router = APIRouter(prefix="/stores", tags=["Stores"])


@router.post("/", response_model=StoreResponseDTO, status_code=201)
async def create_store(
    dto: StoreCreateDTO,
    _: object = Depends(require_vendor_role),
    service: StoreService = Depends(get_store_service),
):
    try:
        return await service.create_store(dto)
    except ConflictException as e:
        raise HTTPException(status_code=409, detail=e.detail)


@router.get("/", response_model=PaginatedResponse[StoreResponseDTO])
async def list_stores(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    owner_id: UUID | None = Query(None),
    service: StoreService = Depends(get_store_service),
):
    return await service.list_stores(page=page, limit=limit, owner_id=owner_id)


@router.get("/owner/{owner_id}", response_model=StoreResponseDTO)
async def get_store_by_owner(
    owner_id: UUID,
    service: StoreService = Depends(get_store_service),
):
    try:
        return await service.get_store_by_owner_id(owner_id)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Store not found for owner")


@router.get("/{store_id}", response_model=StoreResponseDTO)
async def get_store(
    store_id: UUID,
    service: StoreService = Depends(get_store_service),
):
    try:
        return await service.get_store_by_id(store_id)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Store not found")


@router.put("/{store_id}", response_model=StoreResponseDTO)
async def update_store(
    store_id: UUID,
    dto: StoreUpdateDTO,
    _: object = Depends(require_vendor_role),
    service: StoreService = Depends(get_store_service),
):
    try:
        return await service.update_store(store_id, dto)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Store not found")


@router.delete("/{store_id}", status_code=204)
async def delete_store(
    store_id: UUID,
    _: object = Depends(require_vendor_role),
    service: StoreService = Depends(get_store_service),
):
    try:
        await service.delete_store(store_id)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Store not found")


@router.get(
    "/{store_id}/products",
    response_model=PaginatedResponse[ProductResponseDTO],
)
async def list_store_products(
    store_id: UUID,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    category_id: UUID | None = None,
    service: ProductService = Depends(get_product_service),
    store_service: StoreService = Depends(get_store_service),
):
    try:
        await store_service.get_store_by_id(store_id)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Store not found")

    return await service.list_products(
        page=page, limit=limit, store_id=store_id, category_id=category_id
    )


@router.post(
    "/{store_id}/products",
    response_model=ProductResponseDTO,
    status_code=201,
)
async def create_store_product(
    store_id: UUID,
    dto: ProductCreateDTO,
    _: object = Depends(require_vendor_role),
    service: ProductService = Depends(get_product_service),
    store_service: StoreService = Depends(get_store_service),
):
    try:
        await store_service.get_store_by_id(store_id)
        return await service.create_product(store_id=store_id, dto=dto)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/{store_id}/orders",
    response_model=PaginatedResponse[StoreOrderResponseDTO],
)
async def list_store_orders(
    store_id: UUID,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    _: object = Depends(require_vendor_role),
    service: OrderService = Depends(get_order_service),
    store_service: StoreService = Depends(get_store_service),
):
    try:
        await store_service.get_store_by_id(store_id)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Store not found")

    return await service.list_store_orders(store_id=store_id, page=page, limit=limit)


@router.patch(
    "/{store_id}/orders/{store_order_id}/status",
    response_model=StoreOrderResponseDTO,
)
async def update_store_order_status(
    store_id: UUID,
    store_order_id: UUID,
    dto: StoreOrderStatusUpdateDTO,
    _: object = Depends(require_vendor_role),
    service: OrderService = Depends(get_order_service),
):
    try:
        return await service.update_store_order_status(store_order_id, dto)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Store order not found")
