from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional

from app.domain.models.product_image import ProductImage


class ProductImageRepository(ABC):
    @abstractmethod
    async def create(self, image: ProductImage) -> ProductImage:
        pass

    @abstractmethod
    async def list_by_product(self, product_id: UUID) -> list[ProductImage]:
        pass

    @abstractmethod
    async def get_by_id(self, image_id: UUID) -> Optional[ProductImage]:
        pass

    @abstractmethod
    async def delete(self, image_id: UUID) -> None:
        pass

    @abstractmethod
    async def clear_primary(self, product_id: UUID) -> None:
        pass

    @abstractmethod
    async def set_primary(self, image_id: UUID) -> None:
        pass
