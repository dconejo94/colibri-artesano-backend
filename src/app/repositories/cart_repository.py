from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.models.main_order import MainOrder
from app.domain.models.store_order import StoreOrder
from app.domain.models.order_item import OrderItem

class CartRepository(ABC):

    @abstractmethod
    async def get_cart(self, buyer_id: UUID) -> MainOrder | None:
        pass
    
    @abstractmethod
    async def get_store_order(
        self,
        main_order_id: UUID,
        store_id: UUID,
    ) -> StoreOrder | None:
        pass

    @abstractmethod
    async def get_order_item(
        self,
        store_order_id: UUID,
        product_id: UUID,
        variant_id: UUID | None,
    ) -> OrderItem | None:
        pass

    @abstractmethod
    async def create_store_order(
        self,
        store_order: StoreOrder,
    ) -> StoreOrder:
        pass

    @abstractmethod
    async def create_order_item(
        self,
        item: OrderItem,
    ) -> OrderItem:
        pass
