from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.models.event import Event, EventAttendee


class EventRepository(ABC):
    @abstractmethod
    async def create(self, event: Event) -> Event:
        pass

    @abstractmethod
    async def list_events(
        self, page: int, limit: int, user_id: UUID | None = None
    ) -> tuple[list[tuple[Event, int, bool]], int]:
        """Return (event, attendee_count, is_attending) tuples and total count."""
        pass

    @abstractmethod
    async def get_by_id(
        self, event_id: UUID, user_id: UUID | None = None
    ) -> tuple[Event, int, bool] | None:
        pass

    @abstractmethod
    async def add_attendee(self, attendee: EventAttendee) -> EventAttendee:
        pass

    @abstractmethod
    async def remove_attendee(self, event_id: UUID, user_id: UUID) -> bool:
        pass

    @abstractmethod
    async def is_attending(self, event_id: UUID, user_id: UUID) -> bool:
        pass
