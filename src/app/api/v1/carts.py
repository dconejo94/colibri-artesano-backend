from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException

from app.domain.schemas.cart import CartResponseDTO, AddToCartDTO

from app.services.cart_service import CartService
from app.api.deps import get_cart_service
from app.core.exceptions import NotFoundException
from app.core.security import CurrentUser

router = APIRouter(prefix="/cart", tags=["Carts"])


@router.get("/", response_model=CartResponseDTO)
async def get_cart(
    user: CurrentUser,
    service: CartService = Depends(get_cart_service),
):
    try:
        return await service.get_cart(user.id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/addProduct", response_model=CartResponseDTO, status_code=201)
async def add_to_cart(
    dto: AddToCartDTO,
    user: CurrentUser,
    service: CartService = Depends(get_cart_service),
):
    try:
        return await service.add_to_cart(user.id, dto)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete(
    "/removeProduct/{product_id}", response_model=CartResponseDTO, status_code=200
)
async def remove_from_cart(
    product_id: UUID,
    user: CurrentUser,
    store_order_id: UUID = Query(...),
    service: CartService = Depends(get_cart_service),
):
    try:
        return await service.remove_from_cart(user.id, product_id, store_order_id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put(
    "/updateCartItemQuantity/{product_id}",
    response_model=CartResponseDTO,
    status_code=200,
)
async def update_cart_item_quantity_(
    product_id: UUID,
    user: CurrentUser,
    store_order_id: UUID = Query(...),
    quantity: int = Query(...),
    service: CartService = Depends(get_cart_service),
):
    try:
        return await service.update_cart_item(
            user.id, product_id, quantity, store_order_id
        )
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
