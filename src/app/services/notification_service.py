# app/services/notification_service.py
from uuid import UUID
from app.domain.models.notification import Notification
from app.domain.models.fcm_token import FCMToken
from app.domain.schemas.notification import NotificationResponseDTO, NotificationListResponseDTO
from app.repositories.notification_repository import NotificationRepository


class NotificationService:
    def __init__(self, repository: NotificationRepository):
        self.repository = repository

    async def get_notifications(self, user_id: UUID) -> NotificationListResponseDTO:
        notifications = await self.repository.get_by_user_id(user_id)
        response = NotificationListResponseDTO(
            list[notifications],
            size=len(notifications)
        )
        return response

    async def register_fcm_token(self, user_id: UUID, token: str) -> None:
        fcm_token = FCMToken(user_id=user_id, token=token)
        await self.repository.save_fcm_token(fcm_token)
