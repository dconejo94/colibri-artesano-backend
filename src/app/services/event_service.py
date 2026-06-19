from uuid import UUID

from app.domain.models.event import Event, EventAttendee
from app.domain.schemas.event import EventCreateDTO, EventResponseDTO
from app.domain.schemas.paginated_response import PaginatedResponse
from app.repositories.event_repository import EventRepository
from app.core.exceptions import NotFoundException, ConflictException


class EventService:
    def __init__(self, repository: EventRepository):
        self.repository = repository

    def _to_response(
        self, event: Event, attendee_count: int, is_attending: bool
    ) -> EventResponseDTO:
        return EventResponseDTO(
            id=event.id,
            title=event.title,
            description=event.description,
            location=event.location,
            start_at=event.start_at,
            end_at=event.end_at,
            image_url=event.image_url,
            created_by=event.created_by,
            created_at=event.created_at,
            attendee_count=attendee_count,
            is_attending=is_attending,
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
        return self._to_response(created, attendee_count=0, is_attending=False)

    async def list_events(
        self, page: int, limit: int, user_id: UUID
    ) -> PaginatedResponse[EventResponseDTO]:
        rows, total = await self.repository.list_events(page, limit, user_id)
        items = [self._to_response(e, count, attending) for e, count, attending in rows]
        return PaginatedResponse(items=items, page=page, limit=limit, total=total)

    async def get_event(self, event_id: UUID, user_id: UUID) -> EventResponseDTO:
        result = await self.repository.get_by_id(event_id, user_id)
        if result is None:
            raise NotFoundException("Event", str(event_id))
        event, count, attending = result
        return self._to_response(event, count, attending)

    async def attend_event(self, event_id: UUID, user_id: UUID) -> EventResponseDTO:
        result = await self.repository.get_by_id(event_id, user_id)
        if result is None:
            raise NotFoundException("Event", str(event_id))
        event, count, attending = result
        if attending:
            raise ConflictException("Already attending this event")

        await self.repository.add_attendee(
            EventAttendee(event_id=event_id, user_id=user_id)
        )
        return self._to_response(event, count + 1, is_attending=True)

    async def unattend_event(self, event_id: UUID, user_id: UUID) -> None:
        result = await self.repository.get_by_id(event_id, user_id)
        if result is None:
            raise NotFoundException("Event", str(event_id))
        removed = await self.repository.remove_attendee(event_id, user_id)
        if not removed:
            raise NotFoundException("Attendance", str(event_id))
