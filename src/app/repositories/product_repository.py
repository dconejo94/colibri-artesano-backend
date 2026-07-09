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
        search: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
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

    @abstractmethod
    async def get_by_id_for_update(self, product_id: UUID) -> Product | None:
        pass

    @abstractmethod
    async def favorite_product(self, user_id: UUID, product_id: UUID) -> None:
        pass

    @abstractmethod
    async def unfavorite_product(self, user_id: UUID, product_id: UUID) -> None:
        pass

    @abstractmethod
    async def list_favorite_products(
        self, user_id: UUID, page: int, limit: int
    ) -> tuple[list[Product], int]:
        pass
