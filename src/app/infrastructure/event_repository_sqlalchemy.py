from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.event import Event
from app.repositories.event_repository import EventRepository


class SQLAlchemyEventRepository(EventRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, event: Event) -> Event:
        self.db.add(event)
        await self.db.flush()
        await self.db.refresh(event)
        return event

    async def list_events(self, page: int, limit: int) -> tuple[list[Event], int]:
        count_result = await self.db.execute(select(func.count()).select_from(Event))
        total = count_result.scalar() or 0

        result = await self.db.execute(
            select(Event)
            .order_by(Event.start_at.asc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        events = list(result.scalars().all())
        return events, total

    async def get_by_id(self, event_id: UUID) -> Event | None:
        result = await self.db.execute(select(Event).where(Event.id == event_id))
        return result.scalar_one_or_none()
