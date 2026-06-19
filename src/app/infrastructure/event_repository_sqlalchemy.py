from uuid import UUID

from sqlalchemy import select, func, exists
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.event import Event, EventAttendee
from app.repositories.event_repository import EventRepository


class SQLAlchemyEventRepository(EventRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, event: Event) -> Event:
        self.db.add(event)
        await self.db.flush()
        await self.db.refresh(event)
        return event

    async def list_events(
        self, page: int, limit: int, user_id: UUID | None = None
    ) -> tuple[list[tuple[Event, int, bool]], int]:
        attendee_count = (
            select(func.count(EventAttendee.id))
            .where(EventAttendee.event_id == Event.id)
            .correlate(Event)
            .scalar_subquery()
        )

        is_attending = (
            select(
                exists().where(
                    EventAttendee.event_id == Event.id,
                    EventAttendee.user_id == user_id,
                )
            )
            .correlate(Event)
            .scalar_subquery()
            if user_id
            else False
        )

        stmt = select(Event, attendee_count, is_attending)

        count_result = await self.db.execute(select(func.count()).select_from(Event))
        total = count_result.scalar() or 0

        result = await self.db.execute(
            stmt.order_by(Event.start_at.asc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        rows = [(row[0], row[1], bool(row[2])) for row in result.all()]
        return rows, total

    async def get_by_id(
        self, event_id: UUID, user_id: UUID | None = None
    ) -> tuple[Event, int, bool] | None:
        attendee_count = (
            select(func.count(EventAttendee.id))
            .where(EventAttendee.event_id == Event.id)
            .correlate(Event)
            .scalar_subquery()
        )

        is_attending = (
            select(
                exists().where(
                    EventAttendee.event_id == Event.id,
                    EventAttendee.user_id == user_id,
                )
            )
            .correlate(Event)
            .scalar_subquery()
            if user_id
            else False
        )

        result = await self.db.execute(
            select(Event, attendee_count, is_attending).where(Event.id == event_id)
        )
        row = result.first()
        if row is None:
            return None
        return row[0], row[1], bool(row[2])

    async def add_attendee(self, attendee: EventAttendee) -> EventAttendee:
        self.db.add(attendee)
        await self.db.flush()
        await self.db.refresh(attendee)
        return attendee

    async def remove_attendee(self, event_id: UUID, user_id: UUID) -> bool:
        result = await self.db.execute(
            select(EventAttendee).where(
                EventAttendee.event_id == event_id,
                EventAttendee.user_id == user_id,
            )
        )
        attendee = result.scalars().first()
        if attendee is None:
            return False
        await self.db.delete(attendee)
        await self.db.flush()
        return True

    async def is_attending(self, event_id: UUID, user_id: UUID) -> bool:
        result = await self.db.execute(
            select(
                exists().where(
                    EventAttendee.event_id == event_id,
                    EventAttendee.user_id == user_id,
                )
            )
        )
        return bool(result.scalar())
