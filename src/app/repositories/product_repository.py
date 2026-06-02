from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional

from app.domain.models.product import Product


class ProductRepository(ABC):
    @abstractmethod
    async def create(self, product: Product) -> Product:
        pass

    @abstractmethod
    async def list_products(
        self,
        page: int,
        limit: int,
        store_id: UUID | None = None,
        category_id: UUID | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[Product], int]:
        pass

    @abstractmethod
    async def get_by_id(self, product_id: UUID) -> Optional[Product]:
        pass

    @abstractmethod
    async def update(self, product: Product) -> Product:
        pass

    @abstractmethod
    async def delete(self, product: Product) -> None:
        pass
