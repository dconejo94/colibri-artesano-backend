from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models.event import Event, EventParticipant, ParticipationStatus
from app.repositories.event_repository import EventRepository

from datetime import datetime, timezone
from math import radians, sin, cos, sqrt, asin


class SQLAlchemyEventRepository(EventRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    def _haversine(
        self,
        lat1: float,
        lng1: float,
        lat2: float,
        lng2: float,
    ) -> float:
        radius = 6371.0

        dlat = radians(lat2 - lat1)
        dlng = radians(lng2 - lng1)

        a = (
            sin(dlat / 2) ** 2
            + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
        )

        c = 2 * asin(sqrt(a))

        return radius * c

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

    async def list_upcoming(self, page: int, limit: int) -> tuple[list[Event], int]:
        now = datetime.now(timezone.utc)
        count_result = await self.db.execute(
            select(func.count()).select_from(Event).where(Event.event_date >= now)
        )

        total = count_result.scalar() or 0

        result = await self.db.execute(
            select(Event)
            .options(
                selectinload(Event.participants).selectinload(EventParticipant.store)
            )
            .where(Event.event_date >= now)
            .order_by(Event.event_date.asc())
            .offset((page - 1) * limit)
            .limit(limit)
        )

        return list(result.scalars().all()), total

    async def list_nearby(
        self,
        page: int,
        limit: int,
        lat: float,
        lng: float,
        radius_km: float,
    ) -> tuple[list[Event], int]:

        dialect = self.db.bind.dialect.name

        if dialect == "sqlite":
            result = await self.db.execute(
                select(Event).options(
                    selectinload(Event.participants).selectinload(
                        EventParticipant.store
                    )
                )
            )

            events = list(result.scalars().all())

            nearby = [
                event
                for event in events
                if self._haversine(
                    lat,
                    lng,
                    event.latitude,
                    event.longitude,
                )
                <= radius_km
            ]

            total = len(nearby)

            start = (page - 1) * limit
            end = start + limit

            return nearby[start:end], total

        distance = 6371 * func.acos(
            func.cos(func.radians(lat))
            * func.cos(func.radians(Event.latitude))
            * func.cos(func.radians(Event.longitude) - func.radians(lng))
            + func.sin(func.radians(lat)) * func.sin(func.radians(Event.latitude))
        )

        count_result = await self.db.execute(
            select(func.count()).select_from(Event).where(distance <= radius_km)
        )

        total = count_result.scalar() or 0

        result = await self.db.execute(
            select(Event)
            .options(
                selectinload(Event.participants).selectinload(EventParticipant.store)
            )
            .where(distance <= radius_km)
            .order_by(distance)
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
        await self.db.refresh(participant, ["store"])
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
        stmt = (
            select(EventParticipant)
            .options(selectinload(EventParticipant.store))
            .where(EventParticipant.event_id == event_id)
        )
        if status is not None:
            stmt = stmt.where(EventParticipant.status == status)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_participant(
        self, participant: EventParticipant
    ) -> EventParticipant:
        await self.db.flush()
        await self.db.refresh(participant)
        await self.db.refresh(participant, ["store"])
        return participant

    async def delete_participant(self, participant: EventParticipant) -> None:
        await self.db.delete(participant)
        await self.db.flush()
