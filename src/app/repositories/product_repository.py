from abc import ABC, abstractmethod
from app.domain.models import Product


class ProductRepository(ABC):
    @abstractmethod
    def list_products(
        self,
        page: int,
        limit: int,
        category: str | None = None,
    ) -> tuple[list[Product], int]:
        pass
