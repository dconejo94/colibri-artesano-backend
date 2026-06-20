from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime


class FCMTokenDTO(BaseModel):
    token: str


class NotificationResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    body: str
    type: str
    reference_id: UUID | None
    is_read: bool
    created_at: datetime

class NotificationListResponseDTO(BaseModel):
    notifications: list[NotificationResponseDTO]
    size: int
    