from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, model_validator, AwareDatetime


class EventCreateDTO(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    location: str | None = Field(None, max_length=255)
    start_at: AwareDatetime
    end_at: AwareDatetime | None = None
    image_url: str | None = None

    @model_validator(mode="after")
    def end_at_must_be_after_start_at(self) -> "EventCreateDTO":
        if self.end_at is not None and self.end_at <= self.start_at:
            raise ValueError("end_at must be after start_at")
        return self


class EventResponseDTO(BaseModel):
    id: UUID
    title: str
    description: str | None
    location: str | None
    start_at: AwareDatetime
    end_at: AwareDatetime | None
    image_url: str | None
    created_by: UUID

    model_config = {"from_attributes": True}