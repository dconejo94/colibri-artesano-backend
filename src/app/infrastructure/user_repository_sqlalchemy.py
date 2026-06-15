from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models.main_order import MainOrder
from app.domain.models.store_order import StoreOrder
from app.domain.models.user import User
from app.repositories.user_repository import UserRepository


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self.db.execute(
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.store), selectinload(User.orders))
        )
        return result.scalars().first()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.email == email).options(selectinload(User.store))
        )
        return result.scalars().first()

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update(self, user: User, data: dict) -> User:
        for key, value in data.items():
            setattr(user, key, value)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        orders_result = await self.db.execute(
            select(MainOrder).where(MainOrder.buyer_id == user.id)
        )
        for order in orders_result.scalars().all():
            await self.db.delete(order)
        await self.db.flush()

        if user.store:
            store_orders_result = await self.db.execute(
                select(StoreOrder).where(StoreOrder.store_id == user.store.id)
            )
            for so in store_orders_result.scalars().all():
                await self.db.delete(so)
            await self.db.flush()

            await self.db.delete(user.store)
            await self.db.flush()

        await self.db.delete(user)
        await self.db.flush()
