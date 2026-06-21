from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models.user import User
from app.domain.models.main_order import MainOrder
from app.domain.models.store_order import StoreOrder
from app.repositories.order_repository import OrderRepository


class SQLAlchemyOrderRepository(OrderRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_main_order(self, order: MainOrder) -> MainOrder:
        self.db.add(order)
        await self.db.flush()
        await self.db.refresh(order, attribute_names=["store_orders"])
        return order

    async def get_main_order_by_id(self, order_id: UUID):
        result = await self.db.execute(
            select(MainOrder)
            .where(MainOrder.id == order_id)
            .options(
                selectinload(MainOrder.store_orders).selectinload(StoreOrder.items)
            )
        )
        return result.scalars().first()

    async def get_cart_by_buyer(self, buyer_id: UUID):
        result = await self.db.execute(
            select(MainOrder)
            .where(
                MainOrder.buyer_id == buyer_id,
                MainOrder.status == "cart",
            )
            .options(
                selectinload(MainOrder.store_orders).selectinload(StoreOrder.items)
            )
        )
        return result.scalars().first()

    async def list_main_orders_by_buyer(self, buyer_id: UUID, page: int, limit: int):
        stmt = select(MainOrder).where(
            MainOrder.buyer_id == buyer_id,
            MainOrder.status == "placed",
        )

        count_result = await self.db.execute(
            select(func.count()).select_from(stmt.subquery())
        )
        total = count_result.scalar()

        result = await self.db.execute(
            stmt.options(
                selectinload(MainOrder.store_orders).selectinload(StoreOrder.items)
            )
            .order_by(MainOrder.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        items = list(result.scalars().all())
        return items, total

    async def list_store_orders_by_store(self, store_id: UUID, page: int, limit: int):
        stmt = select(StoreOrder).where(StoreOrder.store_id == store_id)

        count_result = await self.db.execute(
            select(func.count()).select_from(stmt.subquery())
        )
        total = count_result.scalar()

        result = await self.db.execute(
            stmt.options(selectinload(StoreOrder.items))
            .order_by(StoreOrder.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        items = list(result.scalars().all())
        return items, total

    async def get_store_order_by_id(self, store_order_id: UUID):
        result = await self.db.execute(
            select(StoreOrder)
            .where(StoreOrder.id == store_order_id)
            .options(selectinload(StoreOrder.items))
        )
        return result.scalars().first()

    async def update_store_order_status(self, store_order: StoreOrder):
        await self.db.flush()
        await self.db.refresh(store_order)
        return store_order

    async def buyer_exists(self, buyer_id: UUID) -> bool:
        result = await self.db.execute(select(func.count()).where(User.id == buyer_id))
        return (result.scalar() or 0) > 0

    async def flush(self) -> None:
        await self.db.flush()
        self.db.expire_all()
