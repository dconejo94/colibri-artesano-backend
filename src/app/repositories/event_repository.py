from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.models.event import Event


class EventRepository(ABC):
    @abstractmethod
    async def create(self, event: Event) -> Event:
        pass

    @abstractmethod
    async def list_events(self, page: int, limit: int) -> tuple[list[Event], int]:
        pass

    @abstractmethod
    async def get_by_id(self, event_id: UUID) -> Event | None:
        pass
