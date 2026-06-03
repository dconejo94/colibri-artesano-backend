from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional

from app.domain.models.product_variant import ProductVariant


class ProductVariantRepository(ABC):
    @abstractmethod
    async def create(self, variant: ProductVariant) -> ProductVariant:
        pass

    @abstractmethod
    async def list_by_product(self, product_id: UUID) -> list[ProductVariant]:
        pass

    @abstractmethod
    async def get_by_id(self, variant_id: UUID) -> Optional[ProductVariant]:
        pass

    @abstractmethod
    async def update(self, variant: ProductVariant) -> ProductVariant:
        pass

    @abstractmethod
    async def delete(self, variant: ProductVariant) -> None:
        pass
