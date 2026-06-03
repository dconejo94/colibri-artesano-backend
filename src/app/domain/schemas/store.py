from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class StoreCreateDTO(BaseModel):
    owner_id: UUID
    name: str
    description: str | None = None
    logo_url: str | None = None


class StoreUpdateDTO(BaseModel):
    name: str | None = None
    description: str | None = None
    logo_url: str | None = None


class StoreResponseDTO(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    description: str | None
    logo_url: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
