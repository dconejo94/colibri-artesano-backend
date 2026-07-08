from uuid import UUID
import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models.store import Store, follows
from app.domain.models.product import Product
from app.domain.models.product_variant import ProductVariant
from app.domain.models.user import User
from app.repositories.store_repository import StoreRepository


class SQLAlchemyStoreRepository(StoreRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, store: Store) -> Store:
        self.db.add(store)
        await self.db.flush()
        await self.db.refresh(store)
        return store

    async def list_stores(self, page: int, limit: int, owner_id: UUID | None = None):
        stmt = select(Store)

        if owner_id:
            stmt = stmt.where(Store.owner_id == owner_id)

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
        result = await self.db.execute(
            select(Store)
            .where(Store.id == store_id)
            .options(
                selectinload(Store.products)
                .selectinload(Product.variants)
                .selectinload(ProductVariant.images)
            )
        )
        return result.scalars().first()

    async def get_by_owner_id(self, owner_id: UUID):
        result = await self.db.execute(select(Store).where(Store.owner_id == owner_id))
        return result.scalars().first()

    async def update(self, store: Store) -> Store:
        await self.db.flush()
        await self.db.refresh(store)
        return store

    async def delete(self, store: Store) -> None:
        await self.db.delete(store)
        await self.db.flush()

    async def get_profile_stats(
        self, store_id: UUID, user_id: UUID | None = None
    ) -> tuple[Store, int, int, bool] | None:
        result = await self.db.execute(select(Store).where(Store.id == store_id))
        store = result.scalars().first()
        if not store:
            return None

        # Products count
        p_count_result = await self.db.execute(
            select(func.count(Product.id)).where(Product.store_id == store_id)
        )
        product_count = p_count_result.scalar() or 0

        # Followers count
        f_count_result = await self.db.execute(
            select(func.count())
            .select_from(follows)
            .where(follows.c.store_id == store_id)
        )
        follower_count = f_count_result.scalar() or 0

        # Is following
        is_following = False
        if user_id:
            is_following = await self.is_following(store_id, user_id)

        return store, product_count, follower_count, is_following

    async def add_follower(self, store_id: UUID, user_id: UUID) -> None:
        stmt = follows.insert().values(
            id=uuid.uuid4(), store_id=store_id, user_id=user_id
        )
        await self.db.execute(stmt)
        await self.db.flush()

    async def remove_follower(self, store_id: UUID, user_id: UUID) -> None:
        stmt = follows.delete().where(
            (follows.c.store_id == store_id) & (follows.c.user_id == user_id)
        )
        await self.db.execute(stmt)
        await self.db.flush()

    async def is_following(self, store_id: UUID, user_id: UUID) -> bool:
        stmt = (
            select(1)
            .select_from(follows)
            .where((follows.c.store_id == store_id) & (follows.c.user_id == user_id))
        )
        result = await self.db.execute(stmt)
        return result.scalar() is not None

    async def get_followers(self, store_id: UUID) -> list[User]:
        stmt = select(User).where(User.followed_stores.any(Store.id == store_id))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_followed_stores(
        self, user_id: UUID, page: int, limit: int
    ) -> tuple[list[Store], int]:
        stmt = select(Store).where(Store.followers.any(User.id == user_id))

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
