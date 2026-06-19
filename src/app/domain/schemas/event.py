from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class EventCreateDTO(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    location: str | None = Field(None, max_length=255)
    start_at: datetime
    end_at: datetime | None = None
    image_url: str | None = None


class EventResponseDTO(BaseModel):
    id: UUID
    title: str
    description: str | None
    location: str | None
    start_at: datetime
    end_at: datetime | None
    image_url: str | None
    created_by: UUID
    created_at: datetime
    attendee_count: int = 0
    is_attending: bool = False

    model_config = {"from_attributes": True}
