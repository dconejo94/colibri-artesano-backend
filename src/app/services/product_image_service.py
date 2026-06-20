from uuid import UUID

from app.domain.models.product_image import ProductImage
from app.domain.schemas.product_image import ProductImageCreateDTO
from app.repositories.product_image_repository import ProductImageRepository
from app.infrastructure.azure_blob_storage import BlobStorageService
from app.core.exceptions import NotFoundException, InvalidImageUrlError


class ProductImageService:
    def __init__(
        self,
        repository: ProductImageRepository,
        blob_storage: BlobStorageService | None = None,
        validate_image_url: bool = False,
    ):
        self.repository = repository
        self.blob_storage = blob_storage
        self.validate_image_url = validate_image_url

    async def add_image(
        self, product_id: UUID, dto: ProductImageCreateDTO
    ) -> ProductImage:
        if (
            self.validate_image_url
            and self.blob_storage is not None
            and not self.blob_storage.is_own_blob_url(dto.image_url)
        ):
            raise InvalidImageUrlError()
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

    async def delete_image(self, product_id: UUID, image_id: UUID) -> None:
        image = await self.repository.get_by_id(image_id)
        if not image or image.product_id != product_id:
            raise NotFoundException("ProductImage", str(image_id))
        image_url = image.image_url
        await self.repository.delete(image)
        if self.blob_storage is not None:
            # Best-effort: never raises, so a missing blob can't fail the delete.
            self.blob_storage.delete_blob(image_url)

    async def set_primary(self, product_id: UUID, image_id: UUID) -> None:
        image = await self.repository.get_by_id(image_id)
        if not image or image.product_id != product_id:
            raise NotFoundException("ProductImage", str(image_id))
        await self.repository.clear_primary(product_id)
        await self.repository.set_primary(image_id)
