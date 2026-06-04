from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models.main_order import MainOrder
from app.domain.models.store_order import StoreOrder
from app.domain.models.order_item import OrderItem
from app.domain.models.product import Product

from app.repositories.cart_repository import CartRepository


class SQLAlchemyCartRepository(CartRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_cart(self, buyer_id: UUID) -> MainOrder | None:
        result = await self.db.execute(
            select(MainOrder)
            .where(
                MainOrder.buyer_id == buyer_id,
                MainOrder.status == "pending",
            )
            .options(
                selectinload(MainOrder.store_orders).selectinload(StoreOrder.store),
                selectinload(MainOrder.store_orders)
                .selectinload(StoreOrder.items)
                .selectinload(OrderItem.product)
                .selectinload(Product.images),
                selectinload(MainOrder.store_orders)
                .selectinload(StoreOrder.items)
                .selectinload(OrderItem.variant),
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
        self, product_id: UUID, cart_id: UUID
    ) -> OrderItem | None:

        result = await self.db.execute(
            select(OrderItem).where(
                OrderItem.store_order_id == cart_id,
                OrderItem.product_id == product_id,
            )
        )

        item = result.scalars().first()

        if item:
            await self.db.delete(item)

        await self.db.flush()

        return item

    async def flush(self) -> None:
        await self.db.flush()
