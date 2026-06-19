from datetime import datetime, timezone
from uuid import UUID

from app.domain.models.event import Event
from app.domain.schemas.event import EventCreateDTO, EventResponseDTO
from app.domain.schemas.paginated_response import PaginatedResponse
from app.repositories.event_repository import EventRepository
from app.core.exceptions import NotFoundException


class EventService:
    def __init__(self, repository: EventRepository):
        self.repository = repository

    def _ensure_tz(self, dt: datetime | None) -> datetime | None:
        if dt is not None and dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    def _to_response(self, event: Event) -> EventResponseDTO:
        return EventResponseDTO(
            id=event.id,
            title=event.title,
            description=event.description,
            location=event.location,
            start_at=self._ensure_tz(event.start_at),
            end_at=self._ensure_tz(event.end_at),
            image_url=event.image_url,
            created_by=event.created_by,
        )

    async def create_event(
        self, creator_id: UUID, dto: EventCreateDTO
    ) -> EventResponseDTO:
        event = Event(
            title=dto.title,
            description=dto.description,
            location=dto.location,
            start_at=dto.start_at,
            end_at=dto.end_at,
            image_url=dto.image_url,
            created_by=creator_id,
        )
        created = await self.repository.create(event)
        return self._to_response(created)

    async def list_events(
        self, page: int, limit: int
    ) -> PaginatedResponse[EventResponseDTO]:
        events, total = await self.repository.list_events(page, limit)
        items = [self._to_response(e) for e in events]
        return PaginatedResponse(items=items, page=page, limit=limit, total=total)

    async def get_event(self, event_id: UUID) -> EventResponseDTO:
        event = await self.repository.get_by_id(event_id)
        if event is None:
            raise NotFoundException("Event", str(event_id))
        return self._to_response(event)
