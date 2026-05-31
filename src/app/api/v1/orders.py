from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException

from app.services.order_service import OrderService
from app.services.product_service import ProductService
from app.api.deps import get_order_service, get_product_service
from app.domain.schemas.order import (
    MainOrderCreateDTO,
    MainOrderResponseDTO,
)
from app.domain.schemas.paginated_response import PaginatedResponse
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=MainOrderResponseDTO, status_code=201)
async def create_order(
    dto: MainOrderCreateDTO,
    service: OrderService = Depends(get_order_service),
):
    try:
        return await service.create_order(dto)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/", response_model=PaginatedResponse[MainOrderResponseDTO])
async def list_buyer_orders(
    buyer_id: UUID = Query(...),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    service: OrderService = Depends(get_order_service),
):
    return await service.list_buyer_orders(
        buyer_id=buyer_id, page=page, limit=limit
    )


@router.get("/{order_id}", response_model=MainOrderResponseDTO)
async def get_order(
    order_id: UUID,
    service: OrderService = Depends(get_order_service),
):
    try:
        return await service.get_order(order_id)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Order not found")
