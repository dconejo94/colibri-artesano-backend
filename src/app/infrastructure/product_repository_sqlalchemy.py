from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models.product import Product
from app.repositories.product_repository import ProductRepository


class SQLAlchemyProductRepository(ProductRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, product: Product) -> Product:
        self.db.add(product)
        await self.db.flush()
        await self.db.refresh(product)
        return product

    async def list_products(
        self,
        page: int,
        limit: int,
        store_id: UUID | None = None,
        category_id: UUID | None = None,
        is_active: bool | None = None,
    ):
        stmt = select(Product)

        if store_id:
            stmt = stmt.where(Product.store_id == store_id)
        if category_id:
            stmt = stmt.where(Product.category_id == category_id)
        if is_active is not None:
            stmt = stmt.where(Product.is_active == is_active)

        count_result = await self.db.execute(
            select(func.count()).select_from(stmt.subquery())
        )
        total = count_result.scalar()

        result = await self.db.execute(
            stmt.options(
                selectinload(Product.store),
                selectinload(Product.category),
                selectinload(Product.images),
                # variants omitted: ProductListDTO does not expose them.
            )
            .order_by(Product.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        items = list(result.scalars().all())
        return items, total

    async def get_by_id(self, product_id: UUID):
        result = await self.db.execute(
            select(Product)
            .where(Product.id == product_id)
            .options(
                selectinload(Product.images),
                selectinload(Product.variants),
                selectinload(Product.store),
                selectinload(Product.category),
            )
        )
        return result.scalars().first()

    async def update(self, product: Product) -> Product:
        await self.db.flush()
        await self.db.refresh(product)
        return product

    async def delete(self, product: Product) -> None:
        await self.db.delete(product)
        await self.db.flush()

    async def get_by_id_for_update(self, product_id: UUID) -> Product | None:
        query = select(Product).where(Product.id == product_id).with_for_update()

        result = await self.db.execute(query)
        return result.scalars().first()
