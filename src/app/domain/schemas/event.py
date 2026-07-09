from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, AwareDatetime

from app.domain.models.event import ParticipationStatus


# ── Nested ────────────────────────────────────────────────────────


class StoreInEventDTO(BaseModel):
    id: UUID
    name: str
    logo_url: str | None

    model_config = {"from_attributes": True}


class ParticipantResponseDTO(BaseModel):
    id: UUID
    event_id: UUID
    store_id: UUID
    store_name: str
    status: ParticipationStatus
    requested_by: UUID
    reviewed_by: UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Events ────────────────────────────────────────────────────────


class EventCreateDTO(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    location: str | None = Field(None, max_length=255)

    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

    event_date: AwareDatetime
    cover_image_url: str | None = None


class EventUpdateDTO(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    location: str | None = Field(None, max_length=255)

    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)

    event_date: AwareDatetime | None = None
    cover_image_url: str | None = None

class EventResponseDTO(BaseModel):
    id: UUID
    title: str
    description: str | None
    location: str | None

    latitude: float
    longitude: float

    event_date: AwareDatetime
    cover_image_url: str | None
    created_by: UUID
    created_at: datetime
    participants: list[StoreInEventDTO] = []
    my_participation: ParticipationStatus | None = None

    model_config = {"from_attributes": True}

# ── Participation ─────────────────────────────────────────────────


class ParticipantReviewDTO(BaseModel):
    status: ParticipationStatus

    model_config = {"from_attributes": True}
