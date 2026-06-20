from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models.category import Category
from app.domain.models.product import Product
from app.domain.models.product_variant import ProductVariant
from app.repositories.category_repository import CategoryRepository


class SQLAlchemyCategoryRepository(CategoryRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, category: Category) -> Category:
        self.db.add(category)
        await self.db.flush()
        await self.db.refresh(category)
        return category

    async def list_all(self) -> list[Category]:
        result = await self.db.execute(select(Category).order_by(Category.name))
        return list(result.scalars().all())

    async def get_by_id(self, category_id: UUID):
        result = await self.db.execute(
            select(Category)
            .where(Category.id == category_id)
            .options(
                selectinload(Category.products)
                .selectinload(Product.variants)
                .selectinload(ProductVariant.images)
            )
        )
        return result.scalars().first()

    async def get_by_slug(self, slug: str):
        result = await self.db.execute(select(Category).where(Category.slug == slug))
        return result.scalars().first()

    async def update(self, category: Category) -> Category:
        await self.db.flush()
        await self.db.refresh(category)
        return category

    async def delete(self, category: Category) -> None:
        await self.db.delete(category)
        await self.db.flush()
