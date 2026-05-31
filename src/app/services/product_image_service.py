from uuid import UUID

from app.domain.models.product_image import ProductImage
from app.domain.schemas.product_image import ProductImageCreateDTO
from app.repositories.product_image_repository import ProductImageRepository
from app.core.exceptions import NotFoundException


class ProductImageService:
    def __init__(self, repository: ProductImageRepository):
        self.repository = repository

    async def add_image(
        self, product_id: UUID, dto: ProductImageCreateDTO
    ) -> ProductImage:
        image = ProductImage(
            product_id=product_id,
            image_url=dto.image_url,
            is_primary=dto.is_primary,
        )
        if dto.is_primary:
            await self.repository.clear_primary(product_id)
        return await self.repository.create(image)

    async def list_images(self, product_id: UUID) -> list[ProductImage]:
        return await self.repository.list_by_product(product_id)

    async def delete_image(self, image_id: UUID) -> None:
        image = await self.repository.get_by_id(image_id)
        if not image:
            raise NotFoundException("ProductImage", str(image_id))
        await self.repository.delete(image_id)

    async def set_primary(self, product_id: UUID, image_id: UUID) -> None:
        image = await self.repository.get_by_id(image_id)
        if not image:
            raise NotFoundException("ProductImage", str(image_id))
        await self.repository.clear_primary(product_id)
        await self.repository.set_primary(image_id)
