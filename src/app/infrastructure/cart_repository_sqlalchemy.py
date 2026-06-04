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
            select(MainOrder).where(
                MainOrder.buyer_id == buyer_id,
                MainOrder.status == "pending",
            )
                .options(
                selectinload(MainOrder.store_orders)
                .selectinload(StoreOrder.store),

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