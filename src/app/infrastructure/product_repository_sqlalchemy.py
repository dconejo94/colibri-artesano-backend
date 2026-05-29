from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.product import Product
from app.repositories.product_repository import ProductRepository


class SQLAlchemyProductRepository(ProductRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_products(self, page: int, limit: int, category: str | None = None):
        stmt = select(Product)

        if category:
            stmt = stmt.where(Product.category == category)

        count_result = await self.db.execute(select(func.count()).select_from(stmt.subquery()))
        total = count_result.scalar()

        result = await self.db.execute(stmt.offset((page - 1) * limit).limit(limit))
        items = result.scalars().all()

        return items, total

    async def get_product_by_id(self, id: int):
        result = await self.db.execute(select(Product).where(Product.id == id))
        return result.scalars().first()
