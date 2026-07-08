from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models.store import Store
from app.repositories.search_repository import StoreSearchRepository


class SQLAlchemyStoreSearchRepository(StoreSearchRepository):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def _base_stmt(self, query: str):
        pattern = f"%{query}%"
        return select(Store).where(
            or_(
                Store.name.ilike(pattern),
                Store.description.ilike(pattern),
            )
        )

    async def search(self, query: str, page: int, limit: int) -> tuple[list[Store], int]:
        if not query.strip():
            return [], 0

        base = self._base_stmt(query)

        count_result = await self.db.execute(
            select(func.count()).select_from(base.subquery())
        )
        total: int = count_result.scalar() or 0

        result = await self.db.execute(
            base.order_by(Store.name)
            .offset((page - 1) * limit)
            .limit(limit)
        )
        items = list(result.scalars().all())
        return items, total

    async def autocomplete(self, query: str, limit: int = 10) -> list[Store]:
        if not query.strip():
            return []

        result = await self.db.execute(
            self._base_stmt(query)
            .order_by(Store.name)
            .limit(limit)
        )
        return list(result.scalars().all())
