from abc import ABC, abstractmethod

from app.domain.models.product import Product
from app.domain.models.store import Store
from app.domain.models.category import Category


class ProductSearchRepository(ABC):
    """Abstract contract for product full-text search.

    Keeping search concerns separate from the general ``ProductRepository``
    makes the dependency explicit and allows any consumer to inject only the
    capability it needs.  A future ``StoreSearchRepository`` or
    ``CategorySearchRepository`` can follow the same pattern without touching
    existing code.
    """

    @abstractmethod
    async def search(
        self,
        query: str,
        page: int,
        limit: int,
        is_active: bool = True,
    ) -> tuple[list[Product], int]:
        """Full-text search over product name and description.

        Returns a ``(items, total_count)`` tuple suitable for building a
        paginated response.  An empty *query* string must return an empty
        result rather than all products.
        """

    @abstractmethod
    async def autocomplete(
        self,
        query: str,
        limit: int = 10,
        is_active: bool = True,
    ) -> list[Product]:
        """Lightweight prefix/trigram search over product name and description.

        Designed to execute in <300 ms.  Returns at most *limit* products
        (hard-capped at 10 by the service layer).  An empty *query* string
        must return an empty list.
        """



class StoreSearchRepository(ABC):
    @abstractmethod
    async def search(
        self, query: str, page: int, limit: int
    ) -> tuple[list[Store], int]:
        pass

    @abstractmethod
    async def autocomplete(self, query: str, limit: int = 10) -> list[Store]:
        pass


class CategorySearchRepository(ABC):
    @abstractmethod
    async def search(self, query: str) -> list[Category]:
        pass

    @abstractmethod
    async def autocomplete(self, query: str, limit: int = 10) -> list[Category]:
        pass
