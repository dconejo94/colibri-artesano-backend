from abc import ABC, abstractmethod


class ProductRepository(ABC):
    @abstractmethod
    def list_products(
        self,
        page: int,
        limit: int,
        category: str | None = None,
    ):
        pass
