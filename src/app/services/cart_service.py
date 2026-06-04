from uuid import UUID

from decimal import Decimal 

from app.domain.schemas.cart import (
    CartItemResponseDTO,
    CartResponseDTO,
    CartStoreResponseDTO
)

from app.repositories.cart_repository import CartRepository
from app.repositories.order_repository import OrderRepository

from app.core.exceptions import NotFoundException


class CartService:
    def __init__(
        self,
        cart_repository: CartRepository,
        order_repository: OrderRepository
    ):
        self.cart_repository = cart_repository
        self.order_repository = order_repository
    
    async def get_cart(self, buyer_id: UUID) -> CartResponseDTO:
        if not await self.order_repository.buyer_exists(buyer_id):
            raise NotFoundException("User", str(buyer_id))
        
        cart = await self.cart_repository.get_cart(buyer_id)

        if not cart:
            return CartResponseDTO(
                order_id=None,
                buyer_id=buyer_id,
                total_amount=Decimal("0.00"),
                stores=[]
            )
        stores = []

        for store_order in cart.store_orders:
            items = []

            for item in store_order.items:
                primary_image = next(
                    (
                        image
                        for image in item.product.images
                        if image.is_primary
                    ),
                    None,
                )

                items.append(
                    CartItemResponseDTO(
                        id=item.id,
                        product_id=item.product.id,
                        product_name=item.product.name,
                        product_image_url=(primary_image.image_url if primary_image else None),
                        variant_id=(
                            item.variant.id if item.variant else None
                        ),
                        variant_name=(
                            item.variant.name if item.variant else None
                        ),
                        variant_value=(
                            item.variant.value if item.variant else None
                        ),
                        quantity=item.quantity,
                        unit_price=item.unit_price,
                        subtotal=item.quantity * item.unit_price,
                    )
                )

            stores.append(
                CartStoreResponseDTO(
                    store_id=store_order.store.id,
                    store_name=store_order.store.name,
                    subtotal_amount=store_order.subtotal_amount,
                    items=items,
                )
            )

        return CartResponseDTO(
            order_id=cart.id,
            buyer_id=cart.buyer_id,
            total_amount=cart.total_amount,
            stores=stores,
        )
        