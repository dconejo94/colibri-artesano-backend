from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.category import Category
from app.repositories.search_repository import CategorySearchRepository


class SQLAlchemyCategorySearchRepository(CategorySearchRepository):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def _base_stmt(self, query: str):
        pattern = f"%{query}%"
        return select(Category).where(
            or_(
                Category.name.ilike(pattern),
                Category.slug.ilike(pattern),
            )
        )

    async def search(self, query: str) -> list[Category]:
        if not query.strip():
            return []

        result = await self.db.execute(self._base_stmt(query).order_by(Category.name))
        return list(result.scalars().all())

    async def autocomplete(self, query: str, limit: int = 10) -> list[Category]:
        if not query.strip():
            return []

        result = await self.db.execute(
            self._base_stmt(query).order_by(Category.name).limit(limit)
        )
        return list(result.scalars().all())
