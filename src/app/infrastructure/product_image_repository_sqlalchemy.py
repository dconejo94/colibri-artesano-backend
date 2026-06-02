from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.product_image import ProductImage
from app.repositories.product_image_repository import ProductImageRepository


class SQLAlchemyProductImageRepository(ProductImageRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, image: ProductImage) -> ProductImage:
        self.db.add(image)
        await self.db.flush()
        await self.db.refresh(image)
        return image

    async def list_by_product(self, product_id: UUID) -> list[ProductImage]:
        result = await self.db.execute(
            select(ProductImage).where(ProductImage.product_id == product_id)
        )
        return list(result.scalars().all())

    async def get_by_id(self, image_id: UUID):
        result = await self.db.execute(
            select(ProductImage).where(ProductImage.id == image_id)
        )
        return result.scalars().first()

    async def delete(self, image: ProductImage) -> None:
        await self.db.delete(image)
        await self.db.flush()

    async def clear_primary(self, product_id: UUID) -> None:
        await self.db.execute(
            update(ProductImage)
            .where(ProductImage.product_id == product_id)
            .values(is_primary=False)
        )
        await self.db.flush()

    async def set_primary(self, image_id: UUID) -> None:
        await self.db.execute(
            update(ProductImage)
            .where(ProductImage.id == image_id)
            .values(is_primary=True)
        )
        await self.db.flush()
