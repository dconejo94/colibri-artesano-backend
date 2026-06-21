from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models.event import Event, EventParticipant, ParticipationStatus
from app.repositories.event_repository import EventRepository


class SQLAlchemyEventRepository(EventRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Events ────────────────────────────────────────────────────

    async def create(self, event: Event) -> Event:
        self.db.add(event)
        await self.db.flush()
        await self.db.refresh(event, ["participants"])
        return event

    async def update(self, event: Event) -> Event:
        await self.db.flush()
        await self.db.refresh(event, ["participants"])
        return event

    async def delete(self, event: Event) -> None:
        await self.db.delete(event)
        await self.db.flush()

    async def list_events(self, page: int, limit: int) -> tuple[list[Event], int]:
        count_result = await self.db.execute(select(func.count()).select_from(Event))
        total = count_result.scalar() or 0

        result = await self.db.execute(
            select(Event)
            .options(
                selectinload(Event.participants).selectinload(EventParticipant.store)
            )
            .order_by(Event.event_date.asc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        return list(result.scalars().all()), total

    async def get_by_id(self, event_id: UUID) -> Event | None:
        result = await self.db.execute(
            select(Event)
            .options(
                selectinload(Event.participants).selectinload(EventParticipant.store)
            )
            .where(Event.id == event_id)
        )
        return result.scalar_one_or_none()

    # ── Participants ──────────────────────────────────────────────

    async def add_participant(self, participant: EventParticipant) -> EventParticipant:
        self.db.add(participant)
        await self.db.flush()
        await self.db.refresh(participant)
        return participant

    async def get_participant(
        self, event_id: UUID, store_id: UUID
    ) -> EventParticipant | None:
        result = await self.db.execute(
            select(EventParticipant).where(
                EventParticipant.event_id == event_id,
                EventParticipant.store_id == store_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_participants(
        self, event_id: UUID, status: ParticipationStatus | None = None
    ) -> list[EventParticipant]:
        stmt = select(EventParticipant).where(EventParticipant.event_id == event_id)
        if status is not None:
            stmt = stmt.where(EventParticipant.status == status)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_participant(
        self, participant: EventParticipant
    ) -> EventParticipant:
        await self.db.flush()
        await self.db.refresh(participant)
        return participant

    async def delete_participant(self, participant: EventParticipant) -> None:
        await self.db.delete(participant)
        await self.db.flush()
