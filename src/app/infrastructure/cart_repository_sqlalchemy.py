from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models.main_order import MainOrder
from app.domain.models.store_order import StoreOrder
from app.domain.models.order_item import OrderItem
from app.domain.models.product_variant import ProductVariant

from app.repositories.cart_repository import CartRepository


class SQLAlchemyCartRepository(CartRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_cart(self, buyer_id: UUID) -> MainOrder | None:
        result = await self.db.execute(
            select(MainOrder)
            .where(
                MainOrder.buyer_id == buyer_id,
                MainOrder.status == "cart",
            )
            .options(
                selectinload(MainOrder.store_orders).selectinload(StoreOrder.store),
                selectinload(MainOrder.store_orders)
                .selectinload(StoreOrder.items)
                .selectinload(OrderItem.product),
                # The line's image comes from its variant now.
                selectinload(MainOrder.store_orders)
                .selectinload(StoreOrder.items)
                .selectinload(OrderItem.variant)
                .selectinload(ProductVariant.images),
            )
        )
        return result.scalars().first()

    async def get_store_order(
        self,
        main_order_id: UUID,
        store_id: UUID,
    ) -> StoreOrder | None:
        result = await self.db.execute(
            select(StoreOrder).where(
                StoreOrder.main_order_id == main_order_id,
                StoreOrder.store_id == store_id,
            )
        )

        return result.scalars().first()

    async def get_order_item(
        self,
        store_order_id: UUID,
        product_id: UUID,
        variant_id: UUID | None,
    ) -> OrderItem | None:

        query = select(OrderItem).where(
            OrderItem.store_order_id == store_order_id,
            OrderItem.product_id == product_id,
        )

        if variant_id is None:
            query = query.where(OrderItem.variant_id.is_(None))
        else:
            query = query.where(OrderItem.variant_id == variant_id)

        result = await self.db.execute(query)

        return result.scalars().first()

    async def create_store_order(self, store_order: StoreOrder) -> StoreOrder:
        self.db.add(store_order)

        await self.db.flush()
        await self.db.refresh(store_order)

        return store_order

    async def create_order_item(self, item: OrderItem) -> OrderItem:
        self.db.add(item)

        await self.db.flush()
        await self.db.refresh(item)

        return item

    async def remove_order_item(
        self,
        product_id: UUID,
        variant_id: UUID | None,
        store_order_id: UUID,
    ) -> OrderItem | None:

        query = select(OrderItem).where(
            OrderItem.store_order_id == store_order_id,
            OrderItem.product_id == product_id,
        )

        if variant_id is None:
            query = query.where(OrderItem.variant_id.is_(None))
        else:
            query = query.where(OrderItem.variant_id == variant_id)

        result = await self.db.execute(query)

        item = result.scalars().first()

        if item:
            await self.db.delete(item)

        await self.db.flush()

        return item

    async def count_store_order_items(self, store_order_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(OrderItem)
            .where(OrderItem.store_order_id == store_order_id)
        )
        return result.scalar() or 0

    async def delete_store_order(self, store_order: StoreOrder) -> None:
        await self.db.delete(store_order)
        await self.db.flush()

    async def count_main_order_store_orders(self, main_order_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(StoreOrder)
            .where(StoreOrder.main_order_id == main_order_id)
        )
        return result.scalar() or 0

    async def delete_main_order(self, main_order: MainOrder) -> None:
        await self.db.delete(main_order)
        await self.db.flush()

    async def flush(self) -> None:
        await self.db.flush()
        self.db.expire_all()
