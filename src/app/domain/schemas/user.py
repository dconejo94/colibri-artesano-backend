from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class UserResponseDTO(BaseModel):
    id: UUID
    email: str
    name: str | None
    phone: str | None
    address: str | None
    avatar_url: str | None
    bio: str | None
    is_active: bool
    is_admin: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdateDTO(BaseModel):
    name: str | None = None
    phone: str | None = None
    address: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
