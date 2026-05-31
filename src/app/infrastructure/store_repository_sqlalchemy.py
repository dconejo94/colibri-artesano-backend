from uuid import UUID

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.store import Store
from app.repositories.store_repository import StoreRepository


class SQLAlchemyStoreRepository(StoreRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, store: Store) -> Store:
        self.db.add(store)
        await self.db.flush()
        await self.db.refresh(store)
        return store

    async def list_stores(self, page: int, limit: int):
        stmt = select(Store)

        count_result = await self.db.execute(
            select(func.count()).select_from(stmt.subquery())
        )
        total = count_result.scalar()

        result = await self.db.execute(
            stmt.order_by(Store.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        items = list(result.scalars().all())
        return items, total

    async def get_by_id(self, store_id: UUID):
        result = await self.db.execute(select(Store).where(Store.id == store_id))
        return result.scalars().first()

    async def get_by_owner_id(self, owner_id: UUID):
        result = await self.db.execute(select(Store).where(Store.owner_id == owner_id))
        return result.scalars().first()

    async def update(self, store: Store) -> Store:
        await self.db.flush()
        await self.db.refresh(store)
        return store

    async def delete(self, store_id: UUID) -> None:
        await self.db.execute(delete(Store).where(Store.id == store_id))
        await self.db.flush()
