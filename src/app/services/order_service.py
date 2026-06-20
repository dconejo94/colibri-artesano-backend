from uuid import UUID

from app.domain.models.main_order import MainOrder
from app.domain.models.store_order import StoreOrder
from app.domain.schemas.order import (
    StoreOrderStatusUpdateDTO,
)
from app.domain.schemas.paginated_response import PaginatedResponse
from app.domain.schemas.order import MainOrderResponseDTO, StoreOrderResponseDTO
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.product_variant_repository import ProductVariantRepository
from app.core.exceptions import NotFoundException, ConflictException


class OrderService:
    def __init__(
        self,
        order_repository: OrderRepository,
        product_repository: ProductRepository,
        variant_repository: ProductVariantRepository,
    ):
        self.order_repo = order_repository
        self.product_repo = product_repository
        self.variant_repo = variant_repository

    async def checkout(self, buyer_id: UUID) -> MainOrder:
        """Convert the buyer's active cart into a placed order.

        The cart already holds the validated, priced items, so checkout only
        verifies stock and transitions the same MainOrder from "cart" to
        "placed". No new order is created.
        """
        cart = await self.order_repo.get_cart_by_buyer(buyer_id)

        has_items = cart is not None and any(
            store_order.items for store_order in cart.store_orders
        )
        if not has_items:
            raise ConflictException("Cart is empty")

        for store_order in cart.store_orders:
            for item in store_order.items:
                variant = await self.variant_repo.get_by_id(item.variant_id)
                if not variant or variant.stock_quantity < item.quantity:
                    raise ConflictException(
                        f"Insufficient stock for variant {item.variant_id}"
                    )

        cart.status = "placed"
        return cart

    async def get_order(self, order_id: UUID) -> MainOrder:
        order = await self.order_repo.get_main_order_by_id(order_id)
        if not order:
            raise NotFoundException("Order", str(order_id))
        return order

    async def list_buyer_orders(
        self, buyer_id: UUID, page: int, limit: int
    ) -> PaginatedResponse[MainOrderResponseDTO]:
        items, total = await self.order_repo.list_main_orders_by_buyer(
            buyer_id, page, limit
        )
        return PaginatedResponse(items=items, page=page, limit=limit, total=total)

    async def list_store_orders(
        self, store_id: UUID, page: int, limit: int
    ) -> PaginatedResponse[StoreOrderResponseDTO]:
        items, total = await self.order_repo.list_store_orders_by_store(
            store_id, page, limit
        )
        return PaginatedResponse(items=items, page=page, limit=limit, total=total)

    async def update_store_order_status(
        self, store_order_id: UUID, dto: StoreOrderStatusUpdateDTO
    ) -> StoreOrder:
        store_order = await self.order_repo.get_store_order_by_id(store_order_id)
        if not store_order:
            raise NotFoundException("StoreOrder", str(store_order_id))
        store_order.seller_status = dto.seller_status
        return await self.order_repo.update_store_order_status(store_order)
