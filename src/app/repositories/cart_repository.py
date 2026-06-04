from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.models.main_order import MainOrder


class CartRepository(ABC):

    @abstractmethod
    async def get_cart(self, buyer_id: UUID) -> MainOrder | None:
        pass
