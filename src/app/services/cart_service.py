from uuid import UUID
from decimal import Decimal

from app.domain.schemas.cart import (
    CartItemResponseDTO,
    CartResponseDTO,
    CartStoreResponseDTO,
    AddToCartDTO,
)
from app.domain.models.main_order import MainOrder
from app.domain.models.store_order import StoreOrder

from app.repositories.cart_repository import CartRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.services.store_order_service import StoreOrderService

from app.core.exceptions import NotFoundException


class CartService:
    """Orchestrates the cart: the cart owns its store orders, and a store order
    owns its product lines (delegated to ``StoreOrderService``).

    The cart finds or creates the buyer's active cart and the right store order
    for a product, then hands the line work to the store order. It keeps the
    cart total, cleans up empty store orders / carts, and guards the cart phase.
    """

    def __init__(
        self,
        cart_repository: CartRepository,
        order_repository: OrderRepository,
        product_repository: ProductRepository,
        store_order_service: StoreOrderService,
    ):
        self.cart_repository = cart_repository
        self.order_repository = order_repository
        self.product_repository = product_repository
        self.store_orders = store_order_service

    async def get_cart(self, buyer_id: UUID) -> CartResponseDTO:
        if not await self._is_user_valid(buyer_id):
            raise NotFoundException("User", str(buyer_id))

        cart = await self.cart_repository.get_cart(buyer_id)

        if not cart:
            return CartResponseDTO(
                order_id=None,
                buyer_id=buyer_id,
                total_amount=Decimal("0.00"),
                stores=[],
            )

        stores = []

        for store_order in cart.store_orders:
            items = []

            for item in store_order.items:
                variant_images = item.variant.images if item.variant else []
                primary_image = next(
                    (image for image in variant_images if image.is_primary),
                    None,
                )

                items.append(
                    CartItemResponseDTO(
                        id=item.id,
                        product_id=item.product.id,
                        product_name=item.product.name,
                        product_image_url=(
                            primary_image.image_url if primary_image else None
                        ),
                        variant_id=(item.variant.id if item.variant else None),
                        variant_name=(item.variant.name if item.variant else None),
                        variant_value=(item.variant.value if item.variant else None),
                        quantity=item.quantity,
                        unit_price=item.unit_price,
                        subtotal=item.quantity * item.unit_price,
                    )
                )

            stores.append(
                CartStoreResponseDTO(
                    id=store_order.id,
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

    async def add_to_cart(self, buyer_id: UUID, dto: AddToCartDTO) -> CartResponseDTO:
        if not await self._is_user_valid(buyer_id):
            raise NotFoundException("User", str(buyer_id))

        product = await self.product_repository.get_by_id(dto.product_id)
        if not product:
            raise NotFoundException("Product", str(dto.product_id))

        variant = await self.store_orders.resolve_variant(
            dto.product_id, dto.variant_id
        )

        cart = await self._ensure_cart(buyer_id)
        store_order = await self._ensure_store_order(cart, product.store_id)

        amount = await self.store_orders.add_product(
            store_order, product, variant, dto.quantity
        )
        cart.total_amount += amount

        await self.cart_repository.flush()

        return await self.get_cart(buyer_id)

    async def remove_from_cart(
        self,
        buyer_id: UUID,
        product_id: UUID,
        variant_id: UUID | None,
        store_order_id: UUID,
    ) -> CartResponseDTO:
        if not await self._is_user_valid(buyer_id):
            raise NotFoundException("User", str(buyer_id))

        product = await self.product_repository.get_by_id(product_id)
        if not product:
            raise NotFoundException("Product", str(product_id))

        variant = await self.store_orders.resolve_variant(product_id, variant_id)

        store_order, main_order = await self._validate_store_order_owner(
            buyer_id, store_order_id
        )

        line = await self.store_orders.get_line(store_order_id, product_id, variant.id)
        if not line:
            raise NotFoundException("OrderItem", str(product_id))

        amount = line.quantity * line.unit_price
        item_count = await self.cart_repository.count_store_order_items(store_order_id)
        store_count = await self.cart_repository.count_main_order_store_orders(
            main_order.id
        )

        # Removing the last line drops its empty store order; removing the last
        # store drops the whole cart. Deleting a parent cascades to its children,
        # so the line is only removed on its own when the store survives.
        if item_count <= 1 and store_count <= 1:
            await self.cart_repository.delete_main_order(main_order)
        elif item_count <= 1:
            await self.cart_repository.delete_store_order(store_order)
            main_order.total_amount = max(
                Decimal("0.00"), main_order.total_amount - amount
            )
        else:
            await self.store_orders.remove_line(store_order, line)
            main_order.total_amount = max(
                Decimal("0.00"), main_order.total_amount - amount
            )

        await self.cart_repository.flush()

        return await self.get_cart(buyer_id)

    async def update_cart_item(
        self,
        buyer_id: UUID,
        product_id: UUID,
        variant_id: UUID | None,
        quantity: int,
        store_order_id: UUID,
    ) -> CartResponseDTO:
        if not await self._is_user_valid(buyer_id):
            raise NotFoundException("User", str(buyer_id))

        product = await self.product_repository.get_by_id(product_id)
        if not product:
            raise NotFoundException("Product", str(product_id))

        variant = await self.store_orders.resolve_variant(product_id, variant_id)

        store_order, main_order = await self._validate_store_order_owner(
            buyer_id, store_order_id
        )

        diff = await self.store_orders.update_quantity(
            store_order, product_id, variant, quantity
        )
        main_order.total_amount = max(Decimal("0.00"), main_order.total_amount + diff)

        await self.cart_repository.flush()

        return await self.get_cart(buyer_id)

    async def _ensure_cart(self, buyer_id: UUID) -> MainOrder:
        cart = await self.cart_repository.get_cart(buyer_id)
        if cart:
            return cart
        return await self.order_repository.create_main_order(
            MainOrder(
                buyer_id=buyer_id,
                total_amount=Decimal("0.00"),
                status="cart",
            )
        )

    async def _ensure_store_order(self, cart: MainOrder, store_id: UUID) -> StoreOrder:
        store_order = await self.cart_repository.get_store_order(cart.id, store_id)
        if store_order:
            return store_order
        return await self.cart_repository.create_store_order(
            StoreOrder(
                main_order_id=cart.id,
                store_id=store_id,
                seller_status="pending",
                subtotal_amount=Decimal("0.00"),
            )
        )

    async def _is_user_valid(self, user_id: UUID) -> bool:
        return await self.order_repository.buyer_exists(user_id)

    async def _validate_store_order_owner(
        self,
        buyer_id: UUID,
        store_order_id: UUID,
    ) -> tuple[StoreOrder, MainOrder]:
        store_order = await self.order_repository.get_store_order_by_id(store_order_id)

        if not store_order:
            raise NotFoundException("Cart", str(store_order_id))

        main_order = await self.order_repository.get_main_order_by_id(
            store_order.main_order_id
        )

        # Only the buyer's active cart is mutable. A placed order is frozen, so a
        # store order outside the cart phase is treated as not found.
        if (
            not main_order
            or main_order.buyer_id != buyer_id
            or main_order.status != "cart"
        ):
            raise NotFoundException("Cart", str(store_order_id))

        return store_order, main_order
