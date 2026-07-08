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


class StorePublicDTO(BaseModel):
    """Safe public projection of a store — omits ``owner_id``.

    Used in list endpoints (e.g. ``GET /products/``) where exposing the
    internal owner identifier would be a data-minimization concern.
    """

    id: UUID
    name: str
    description: str | None
    logo_url: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class StoreResponseDTO(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    description: str | None
    logo_url: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class StoreAutocompleteDTO(BaseModel):
    id: UUID
    name: str
    logo_url: str | None = None

    model_config = {"from_attributes": True}
