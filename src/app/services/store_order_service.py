from uuid import UUID
from decimal import Decimal

from app.domain.models.order_item import OrderItem
from app.domain.models.product import Product
from app.domain.models.product_variant import ProductVariant
from app.domain.models.store_order import StoreOrder

from app.repositories.cart_repository import CartRepository
from app.repositories.product_variant_repository import ProductVariantRepository

from app.core.exceptions import NotFoundException, ConflictException


class StoreOrderService:
    """Owns the product lines of a single store order.

    A store order is the per-store order inside a cart; this service is the
    authority over its ``OrderItem`` lines — resolving the variant, enforcing
    stock, pricing the line, and adding/updating/removing it. The cart
    orchestrates which store order a line belongs to; it does not touch lines
    itself.
    """

    def __init__(
        self,
        cart_repository: CartRepository,
        variant_repository: ProductVariantRepository,
    ):
        self.cart_repository = cart_repository
        self.variant_repository = variant_repository

    async def get_line(
        self,
        store_order_id: UUID,
        product_id: UUID,
        variant_id: UUID,
    ) -> OrderItem | None:
        return await self.cart_repository.get_order_item(
            store_order_id, product_id, variant_id
        )

    async def add_product(
        self,
        store_order: StoreOrder,
        product: Product,
        variant: ProductVariant,
        quantity: int,
    ) -> Decimal:
        """Add (or accumulate) a product line. Returns the amount added."""
        unit_price = Decimal(str(product.base_price)) + Decimal(
            str(variant.price_modifier)
        )

        existing = await self.cart_repository.get_order_item(
            store_order.id, product.id, variant.id
        )

        current_quantity = existing.quantity if existing else 0
        if current_quantity + quantity > variant.stock_quantity:
            raise ConflictException(f"Insufficient stock for variant '{variant.id}'")

        if existing:
            existing.quantity += quantity
        else:
            await self.cart_repository.create_order_item(
                OrderItem(
                    store_order_id=store_order.id,
                    product_id=product.id,
                    variant_id=variant.id,
                    quantity=quantity,
                    unit_price=unit_price,
                )
            )

        amount = unit_price * quantity
        store_order.subtotal_amount += amount
        return amount

    async def update_quantity(
        self,
        store_order: StoreOrder,
        product_id: UUID,
        variant: ProductVariant,
        quantity: int,
    ) -> Decimal:
        """Set a line's quantity. Returns the signed amount delta."""
        line = await self.cart_repository.get_order_item(
            store_order.id, product_id, variant.id
        )

        if not line:
            raise NotFoundException("OrderItem", str(product_id))

        if quantity > variant.stock_quantity:
            raise ConflictException(f"Insufficient stock for variant '{variant.id}'")

        old_amount = line.quantity * line.unit_price
        line.quantity = quantity
        diff = (quantity * line.unit_price) - old_amount

        store_order.subtotal_amount = max(
            Decimal("0.00"), store_order.subtotal_amount + diff
        )
        return diff

    async def remove_line(self, store_order: StoreOrder, line: OrderItem) -> Decimal:
        """Remove a line. Returns the amount removed."""
        amount = line.quantity * line.unit_price
        await self.cart_repository.remove_order_item(
            line.product_id, line.variant_id, store_order.id
        )
        store_order.subtotal_amount = max(
            Decimal("0.00"), store_order.subtotal_amount - amount
        )
        return amount

    async def resolve_variant(
        self, product_id: UUID, variant_id: UUID | None
    ) -> ProductVariant:
        """Resolve the variant a line targets.

        Every line targets a concrete variant (the unit that carries stock and
        price). If the caller names a variant, validate it. Otherwise fall back
        to the product's single variant, or require an explicit choice when the
        product has several.
        """
        if variant_id is not None:
            return await self._validate_variant_is_valid(product_id, variant_id)

        variants = await self.variant_repository.list_by_product(product_id)
        if len(variants) == 1:
            return variants[0]
        if not variants:
            raise ConflictException(f"Product '{product_id}' has no variants")
        raise ConflictException(
            f"Product '{product_id}' has multiple variants; variant_id is required"
        )

    async def _validate_variant_is_valid(
        self, product_id: UUID, variant_id: UUID
    ) -> ProductVariant:
        variant = await self.variant_repository.get_by_id(variant_id)

        if not variant or variant.product_id != product_id:
            raise NotFoundException("ProductVariant", str(variant_id))

        return variant
