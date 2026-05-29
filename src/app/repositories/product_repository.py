from abc import ABC, abstractmethod
from app.domain.models import Product

from typing import Optional


class ProductRepository(ABC):
    @abstractmethod
    async def list_products(
        self,
        page: int,
        limit: int,
        category: str | None = None,
    ) -> tuple[list[Product], int]:
        pass

    @abstractmethod
    async def get_product_by_id(self, id: int) -> Optional[Product]:
        pass
