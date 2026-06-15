from uuid import UUID
from decimal import Decimal

from app.domain.models.main_order import MainOrder
from app.domain.models.store_order import StoreOrder
from app.domain.models.order_item import OrderItem
from app.domain.schemas.order import (
    MainOrderCreateDTO,
    StoreOrderStatusUpdateDTO,
)
from app.domain.schemas.paginated_response import PaginatedResponse
from app.domain.schemas.order import MainOrderResponseDTO, StoreOrderResponseDTO
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.product_variant_repository import ProductVariantRepository
from app.core.exceptions import NotFoundException


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

    async def create_order(self, buyer_id: UUID, dto: MainOrderCreateDTO) -> MainOrder:
        if not await self.order_repo.buyer_exists(buyer_id):
            raise NotFoundException("User", str(buyer_id))

        store_groups: dict[UUID, list] = {}

        for item_dto in dto.items:
            product = await self.product_repo.get_by_id(item_dto.product_id)
            if not product:
                raise NotFoundException("Product", str(item_dto.product_id))

            unit_price = Decimal(str(product.base_price))

            if item_dto.variant_id:
                variant = await self.variant_repo.get_by_id(item_dto.variant_id)
                if not variant or variant.product_id != product.id:
                    raise NotFoundException("ProductVariant", str(item_dto.variant_id))
                unit_price += Decimal(str(variant.price_modifier))

            store_id = product.store_id
            store_groups.setdefault(store_id, []).append((item_dto, unit_price))

        total_amount = Decimal("0")
        store_orders = []

        for store_id, grouped_items in store_groups.items():
            subtotal = Decimal("0")
            order_items = []

            for item_dto, unit_price in grouped_items:
                line_total = unit_price * item_dto.quantity
                subtotal += line_total
                order_items.append(
                    OrderItem(
                        product_id=item_dto.product_id,
                        variant_id=item_dto.variant_id,
                        quantity=item_dto.quantity,
                        unit_price=unit_price,
                    )
                )

            store_order = StoreOrder(
                store_id=store_id,
                seller_status="pending",
                subtotal_amount=subtotal,
                items=order_items,
            )
            store_orders.append(store_order)
            total_amount += subtotal

        main_order = MainOrder(
            buyer_id=buyer_id,
            total_amount=total_amount,
            status="pending",
            store_orders=store_orders,
        )
        return await self.order_repo.create_main_order(main_order)

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
