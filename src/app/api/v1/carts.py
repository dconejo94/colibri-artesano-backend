from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException

from app.domain.schemas.cart import CartResponseDTO, AddToCartDTO

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


@router.post("/addProduct", response_model=CartResponseDTO, status_code=201)
async def add_to_cart(
    dto: AddToCartDTO,
    buyer_id: UUID = Query(...),
    service: CartService = Depends(get_cart_service),
):
    try:
        return await service.add_to_cart(buyer_id, dto)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete(
    "/removeProduct/{product_id}", response_model=CartResponseDTO, status_code=200
)
async def remove_from_cart(
    product_id: UUID,
    buyer_id: UUID = Query(...),
    store_order_id: UUID = Query(...),
    service: CartService = Depends(get_cart_service),
):
    try:
        return await service.remove_from_cart(buyer_id, product_id, store_order_id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put(
    "/updateCartItem/{product_id}", response_model=CartResponseDTO, status_code=200
)
async def update_cart_item_(
    product_id: UUID,
    buyer_id: UUID = Query(...),
    store_order_id: UUID = Query(...),
    quantity: int = Query(...),
    service: CartService = Depends(get_cart_service), 
):
    try:
        return await service.update_cart_item(buyer_id, product_id, quantity, store_order_id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))