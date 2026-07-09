from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.models.event import Event, EventParticipant, ParticipationStatus


class EventRepository(ABC):
    # ── Events ────────────────────────────────────────────────────

    @abstractmethod
    async def create(self, event: Event) -> Event:
        pass

    @abstractmethod
    async def update(self, event: Event) -> Event:
        pass

    @abstractmethod
    async def delete(self, event: Event) -> None:
        pass

    @abstractmethod
    async def list_events(self, page: int, limit: int) -> tuple[list[Event], int]:
        pass

    @abstractmethod
    async def list_upcoming(self, page: int, limit: int) -> tuple[list[Event], int]:
        pass

    @abstractmethod
    async def list_nearby(
        self,
        page: int,
        limit: int,
        lat: float,
        lng: float,
        radius_km: float,
    ) -> tuple[list[Event], int]:
        pass

    @abstractmethod
    async def get_by_id(self, event_id: UUID) -> Event | None:
        pass

    # ── Participants ──────────────────────────────────────────────

    @abstractmethod
    async def add_participant(self, participant: EventParticipant) -> EventParticipant:
        pass

    @abstractmethod
    async def get_participant(
        self, event_id: UUID, store_id: UUID
    ) -> EventParticipant | None:
        pass

    @abstractmethod
    async def list_participants(
        self, event_id: UUID, status: ParticipationStatus | None = None
    ) -> list[EventParticipant]:
        pass

    @abstractmethod
    async def update_participant(
        self, participant: EventParticipant
    ) -> EventParticipant:
        pass

    @abstractmethod
    async def delete_participant(self, participant: EventParticipant) -> None:
        pass
