from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.services.order_service import OrderService
from app.api.deps import get_order_service
from app.core.security import CurrentUser
from app.domain.schemas.order import (
    MainOrderResponseDTO,
)
from app.domain.schemas.paginated_response import PaginatedResponse

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=MainOrderResponseDTO, status_code=201)
async def checkout(
    current_user: CurrentUser,
    service: OrderService = Depends(get_order_service),
):
    """Place an order from the buyer's current cart."""
    return await service.checkout(current_user.id)


@router.get("/", response_model=PaginatedResponse[MainOrderResponseDTO])
async def list_buyer_orders(
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    service: OrderService = Depends(get_order_service),
):
    return await service.list_buyer_orders(
        buyer_id=current_user.id, page=page, limit=limit
    )


@router.get("/{order_id}", response_model=MainOrderResponseDTO)
async def get_order(
    order_id: UUID,
    current_user: CurrentUser,
    service: OrderService = Depends(get_order_service),
):
    return await service.get_order(order_id, current_user.id)
