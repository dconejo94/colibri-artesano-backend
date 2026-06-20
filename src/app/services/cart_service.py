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
from app.domain.models.order_item import OrderItem
from app.domain.models.product_variant import ProductVariant

from app.repositories.cart_repository import CartRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.product_variant_repository import ProductVariantRepository

from app.core.exceptions import NotFoundException


class CartService:
    def __init__(
        self,
        cart_repository: CartRepository,
        order_repository: OrderRepository,
        product_repository: ProductRepository,
        variant_repository: ProductVariantRepository,
    ):
        self.cart_repository = cart_repository
        self.order_repository = order_repository
        self.product_repository = product_repository
        self.variant_repository = variant_repository

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
                primary_image = next(
                    (image for image in item.product.images if image.is_primary),
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

        variant = None
        if dto.variant_id:
            variant = await self._validate_variant_is_valid(
                dto.product_id, dto.variant_id
            )

        cart = await self.cart_repository.get_cart(buyer_id)

        if not cart:
            cart = await self.order_repository.create_main_order(
                MainOrder(
                    buyer_id=buyer_id,
                    total_amount=Decimal("0.00"),
                    status="cart",
                )
            )

        store_order = await self.cart_repository.get_store_order(
            cart.id,
            product.store_id,
        )

        if not store_order:
            store_order = await self.cart_repository.create_store_order(
                StoreOrder(
                    main_order_id=cart.id,
                    store_id=product.store_id,
                    seller_status="pending",
                    subtotal_amount=Decimal("0.00"),
                )
            )

        unit_price = Decimal(str(product.base_price))

        if variant:
            unit_price += Decimal(str(variant.price_modifier))

        existing_item = await self.cart_repository.get_order_item(
            store_order.id,
            dto.product_id,
            dto.variant_id,
        )

        if existing_item:
            existing_item.quantity += dto.quantity
        else:
            await self.cart_repository.create_order_item(
                OrderItem(
                    store_order_id=store_order.id,
                    product_id=product.id,
                    variant_id=dto.variant_id,
                    quantity=dto.quantity,
                    unit_price=unit_price,
                )
            )

        total = unit_price * dto.quantity

        store_order.subtotal_amount += total
        cart.total_amount += total

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
            raise NotFoundException(
                "Product",
                str(product_id),
            )

        if variant_id is not None:
            await self._validate_variant_is_valid(product_id, variant_id)

        store_order, main_order = await self._validate_store_order_owner(
            buyer_id, store_order_id
        )

        item = await self.cart_repository.remove_order_item(
            product_id,
            variant_id,
            store_order_id,
        )

        if not item:
            raise NotFoundException(
                "OrderItem",
                str(product_id),
            )

        amount = item.quantity * item.unit_price

        store_order.subtotal_amount = max(
            Decimal("0.00"), store_order.subtotal_amount - amount
        )

        main_order.total_amount = max(Decimal("0.00"), main_order.total_amount - amount)

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

        store_order, main_order = await self._validate_store_order_owner(
            buyer_id, store_order_id
        )

        existing_item = await self.cart_repository.get_order_item_by_product(
            store_order_id,
            product_id,
        )

        if not existing_item:
            raise NotFoundException("OrderItem", str(product_id))

        old_amount = existing_item.quantity * existing_item.unit_price

        effective_variant_id = (
            variant_id if variant_id is not None else existing_item.variant_id
        )

        variant = None
        if effective_variant_id is not None:
            variant = await self._validate_variant_is_valid(
                product_id, effective_variant_id
            )

        unit_price = Decimal(str(product.base_price))
        if variant:
            unit_price += Decimal(str(variant.price_modifier))

        existing_item.variant_id = effective_variant_id
        existing_item.quantity = quantity
        existing_item.unit_price = unit_price

        new_amount = quantity * unit_price
        diff = new_amount - old_amount

        store_order.subtotal_amount = max(
            Decimal("0.00"),
            store_order.subtotal_amount + diff,
        )

        main_order.total_amount = max(
            Decimal("0.00"),
            main_order.total_amount + diff,
        )

        await self.cart_repository.flush()

        return await self.get_cart(buyer_id)

    async def _is_user_valid(self, user_id: UUID) -> bool:
        return await self.order_repository.buyer_exists(user_id)

    async def _validate_store_order_owner(
        self,
        buyer_id: UUID,
        store_order_id: UUID,
    ) -> tuple[StoreOrder, MainOrder]:
        store_order = await self.order_repository.get_store_order_by_id(store_order_id)

        if not store_order:
            raise NotFoundException(
                "Cart",
                str(store_order_id),
            )

        main_order = await self.order_repository.get_main_order_by_id(
            store_order.main_order_id
        )

        if not main_order or main_order.buyer_id != buyer_id:
            raise NotFoundException(
                "Cart",
                str(store_order_id),
            )

        return store_order, main_order

    async def _validate_variant_is_valid(
        self, product_id: UUID, variant_id: UUID
    ) -> ProductVariant:
        variant = await self.variant_repository.get_by_id(variant_id)

        if not variant:
            raise NotFoundException(
                "ProductVariant",
                str(variant_id),
            )

        if variant.product_id != product_id:
            raise NotFoundException(
                "ProductVariant",
                str(variant_id),
            )

        return variant
