from datetime import datetime, timezone
from uuid import UUID

from app.domain.models.event import Event, EventParticipant, ParticipationStatus
from app.domain.schemas.event import (
    EventCreateDTO,
    EventUpdateDTO,
    EventResponseDTO,
    ParticipantReviewDTO,
    StoreInEventDTO,
    ParticipantResponseDTO,
)
from app.domain.schemas.paginated_response import PaginatedResponse
from app.repositories.event_repository import EventRepository
from app.core.exceptions import NotFoundException, ConflictException, ForbiddenException


class EventService:
    def __init__(self, repository: EventRepository):
        self.repository = repository

    # ── Helpers ───────────────────────────────────────────────────

    def _ensure_tz(self, dt: datetime | None) -> datetime | None:
        if dt is not None and dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    def _to_response(
        self,
        event: Event,
        user_role: str | None = None,
        user_store_id: UUID | None = None,
    ) -> EventResponseDTO:
        approved = [
            StoreInEventDTO(
                id=p.store.id,
                name=p.store.name,
                logo_url=p.store.logo_url,
            )
            for p in event.participants
            if p.status == ParticipationStatus.approved
        ]

        my_participation = None
        if user_role == "vendor" and user_store_id is not None:
            match = next(
                (p for p in event.participants if p.store_id == user_store_id), None
            )
            if match:
                my_participation = match.status

        return EventResponseDTO(
            id=event.id,
            title=event.title,
            description=event.description,
            location=event.location,
            event_date=self._ensure_tz(event.event_date),
            cover_image_url=event.cover_image_url,
            created_by=event.created_by,
            created_at=self._ensure_tz(event.created_at),
            participants=approved,
            my_participation=my_participation,
        )

    # ── Events ────────────────────────────────────────────────────

    async def create_event(
        self, creator_id: UUID, dto: EventCreateDTO
    ) -> EventResponseDTO:
        event = Event(
            title=dto.title,
            description=dto.description,
            location=dto.location,
            event_date=dto.event_date,
            cover_image_url=dto.cover_image_url,
            created_by=creator_id,
        )
        created = await self.repository.create(event)
        return self._to_response(created)

    async def list_events(
        self,
        page: int,
        limit: int,
        user_role: str | None = None,
        user_store_id: UUID | None = None,
    ) -> PaginatedResponse[EventResponseDTO]:
        events, total = await self.repository.list_events(page, limit)
        items = [self._to_response(e, user_role, user_store_id) for e in events]
        return PaginatedResponse(items=items, page=page, limit=limit, total=total)

    async def get_event(
        self,
        event_id: UUID,
        user_role: str | None = None,
        user_store_id: UUID | None = None,
    ) -> EventResponseDTO:
        event = await self.repository.get_by_id(event_id)
        if event is None:
            raise NotFoundException("Event", str(event_id))
        return self._to_response(event, user_role, user_store_id)

    async def update_event(
        self, event_id: UUID, dto: EventUpdateDTO
    ) -> EventResponseDTO:
        event = await self.repository.get_by_id(event_id)
        if event is None:
            raise NotFoundException("Event", str(event_id))
        if dto.title is not None:
            event.title = dto.title
        if dto.description is not None:
            event.description = dto.description
        if dto.location is not None:
            event.location = dto.location
        if dto.event_date is not None:
            event.event_date = dto.event_date
        if dto.cover_image_url is not None:
            event.cover_image_url = dto.cover_image_url
        updated = await self.repository.update(event)
        return self._to_response(updated)

    async def delete_event(self, event_id: UUID) -> None:
        event = await self.repository.get_by_id(event_id)
        if event is None:
            raise NotFoundException("Event", str(event_id))
        await self.repository.delete(event)

    # ── Participants ──────────────────────────────────────────────

    async def request_participation(
        self, event_id: UUID, store_id: UUID, requested_by: UUID
    ) -> ParticipantResponseDTO:
        event = await self.repository.get_by_id(event_id)
        if event is None:
            raise NotFoundException("Event", str(event_id))

        existing = await self.repository.get_participant(event_id, store_id)
        if existing is not None:
            raise ConflictException("Store is already registered for this event")

        participant = EventParticipant(
            event_id=event_id,
            store_id=store_id,
            requested_by=requested_by,
            status=ParticipationStatus.pending,
        )
        created = await self.repository.add_participant(participant)
        return ParticipantResponseDTO.model_validate(created)

    async def withdraw_participation(
        self, event_id: UUID, store_id: UUID, user_id: UUID
    ) -> None:
        participant = await self.repository.get_participant(event_id, store_id)
        if participant is None:
            raise NotFoundException("Participation", str(store_id))
        if participant.requested_by != user_id:
            raise ForbiddenException("You do not own this participation request")
        await self.repository.delete_participant(participant)

    async def list_participants(self, event_id: UUID) -> list[ParticipantResponseDTO]:
        event = await self.repository.get_by_id(event_id)
        if event is None:
            raise NotFoundException("Event", str(event_id))
        participants = await self.repository.list_participants(event_id)
        return [ParticipantResponseDTO.model_validate(p) for p in participants]

    async def review_participation(
        self,
        event_id: UUID,
        store_id: UUID,
        reviewed_by: UUID,
        dto: ParticipantReviewDTO,
    ) -> ParticipantResponseDTO:
        participant = await self.repository.get_participant(event_id, store_id)
        if participant is None:
            raise NotFoundException("Participation", str(store_id))
        participant.status = dto.status
        participant.reviewed_by = reviewed_by
        updated = await self.repository.update_participant(participant)
        return ParticipantResponseDTO.model_validate(updated)
