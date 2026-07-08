from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional

from app.domain.models.main_order import MainOrder
from app.domain.models.store_order import StoreOrder


class OrderRepository(ABC):
    @abstractmethod
    async def create_main_order(self, order: MainOrder) -> MainOrder:
        pass

    @abstractmethod
    async def get_main_order_by_id(self, order_id: UUID) -> Optional[MainOrder]:
        pass

    @abstractmethod
    async def get_cart_by_buyer(self, buyer_id: UUID) -> Optional[MainOrder]:
        pass

    @abstractmethod
    async def list_main_orders_by_buyer(
        self, buyer_id: UUID, page: int, limit: int
    ) -> tuple[list[MainOrder], int]:
        pass

    @abstractmethod
    async def list_store_orders_by_store(
        self, store_id: UUID, page: int, limit: int
    ) -> tuple[list[StoreOrder], int]:
        pass

    @abstractmethod
    async def get_store_order_by_id(self, store_order_id: UUID) -> Optional[StoreOrder]:
        pass

    @abstractmethod
    async def update_store_order_status(self, store_order: StoreOrder) -> StoreOrder:
        pass

    @abstractmethod
    async def buyer_exists(self, buyer_id: UUID) -> bool:
        pass

    @abstractmethod
    async def flush(self) -> None:
        pass
