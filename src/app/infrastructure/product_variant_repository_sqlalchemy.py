from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.product_variant import ProductVariant
from app.repositories.product_variant_repository import ProductVariantRepository


class SQLAlchemyProductVariantRepository(ProductVariantRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, variant: ProductVariant) -> ProductVariant:
        self.db.add(variant)
        await self.db.flush()
        await self.db.refresh(variant)
        return variant

    async def list_by_product(self, product_id: UUID) -> list[ProductVariant]:
        result = await self.db.execute(
            select(ProductVariant).where(ProductVariant.product_id == product_id)
        )
        return list(result.scalars().all())

    async def get_by_id(self, variant_id: UUID):
        result = await self.db.execute(
            select(ProductVariant).where(ProductVariant.id == variant_id)
        )
        return result.scalars().first()

    async def update(self, variant: ProductVariant) -> ProductVariant:
        await self.db.flush()
        await self.db.refresh(variant)
        return variant

    async def delete(self, variant_id: UUID) -> None:
        await self.db.execute(
            delete(ProductVariant).where(ProductVariant.id == variant_id)
        )
        await self.db.flush()
