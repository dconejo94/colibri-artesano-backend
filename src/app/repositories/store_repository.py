from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional

from app.domain.models.store import Store
from app.domain.models.user import User


class StoreRepository(ABC):
    @abstractmethod
    async def create(self, store: Store) -> Store:
        pass

    @abstractmethod
    async def list_stores(
        self, page: int, limit: int, owner_id: UUID | None = None
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
    async def delete(self, store: Store) -> None:
        pass

    @abstractmethod
    async def get_profile_stats(
        self, store_id: UUID, user_id: UUID | None = None
    ) -> tuple[Store, int, int, bool] | None:
        pass

    @abstractmethod
    async def add_follower(self, store_id: UUID, user_id: UUID) -> None:
        pass

    @abstractmethod
    async def remove_follower(self, store_id: UUID, user_id: UUID) -> None:
        pass

    @abstractmethod
    async def is_following(self, store_id: UUID, user_id: UUID) -> bool:
        pass

    @abstractmethod
    async def get_followers(self, store_id: UUID) -> list[User]:
        pass

    @abstractmethod
    async def list_followed_stores(
        self, user_id: UUID, page: int, limit: int
    ) -> tuple[list[Store], int]:
        pass
