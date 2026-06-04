from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException

from app.domain.schemas.cart import (
    CartResponseDTO,
)

from app.services.cart_service import CartService
from app.api.deps import get_cart_service
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/cart", tags=["Carts"])

@router.get("/", response_model=CartResponseDTO)
async def get_cart(
    buyer_id: UUID = Query(...),
    service: CartService = Depends(get_cart_service),
):
    try:
        return await service.get_cart(buyer_id=buyer_id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))