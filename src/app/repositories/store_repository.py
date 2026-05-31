from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional

from app.domain.models.store import Store


class StoreRepository(ABC):
    @abstractmethod
    async def create(self, store: Store) -> Store:
        pass

    @abstractmethod
    async def list_stores(
        self, page: int, limit: int
    ) -> tuple[list[Store], int]:
        pass

    @abstractmethod
    async def get_by_id(self, store_id: UUID) -> Optional[Store]:
        pass

    @abstractmethod
    async def get_by_owner_id(self, owner_id: UUID) -> Optional[Store]:
        pass

    @abstractmethod
    async def update(self, store: Store) -> Store:
        pass

    @abstractmethod
    async def delete(self, store_id: UUID) -> None:
        pass
