from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional

from app.domain.models.category import Category


class CategoryRepository(ABC):
    @abstractmethod
    async def create(self, category: Category) -> Category:
        pass

    @abstractmethod
    async def list_all(self) -> list[Category]:
        pass

    @abstractmethod
    async def get_by_id(self, category_id: UUID) -> Optional[Category]:
        pass

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Optional[Category]:
        pass

    @abstractmethod
    async def update(self, category: Category) -> Category:
        pass

    @abstractmethod
    async def delete(self, category_id: UUID) -> None:
        pass
