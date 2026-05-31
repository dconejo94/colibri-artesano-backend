from uuid import UUID

from app.domain.models.product_variant import ProductVariant
from app.domain.schemas.product_variant import (
    ProductVariantCreateDTO,
    ProductVariantUpdateDTO,
)
from app.repositories.product_variant_repository import ProductVariantRepository
from app.core.exceptions import NotFoundException


class ProductVariantService:
    def __init__(self, repository: ProductVariantRepository):
        self.repository = repository

    async def create_variant(
        self, product_id: UUID, dto: ProductVariantCreateDTO
    ) -> ProductVariant:
        variant = ProductVariant(
            product_id=product_id,
            name=dto.name,
            value=dto.value,
            price_modifier=dto.price_modifier,
            stock_quantity=dto.stock_quantity,
        )
        return await self.repository.create(variant)

    async def list_variants(self, product_id: UUID) -> list[ProductVariant]:
        return await self.repository.list_by_product(product_id)

    async def update_variant(
        self, variant_id: UUID, dto: ProductVariantUpdateDTO
    ) -> ProductVariant:
        variant = await self.repository.get_by_id(variant_id)
        if not variant:
            raise NotFoundException("ProductVariant", str(variant_id))

        update_data = dto.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(variant, field, value)

        return await self.repository.update(variant)

    async def delete_variant(self, variant_id: UUID) -> None:
        variant = await self.repository.get_by_id(variant_id)
        if not variant:
            raise NotFoundException("ProductVariant", str(variant_id))
        await self.repository.delete(variant_id)
