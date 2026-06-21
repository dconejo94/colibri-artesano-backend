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
        
        return NotificationListResponseDTO(
            notifications=[NotificationResponseDTO.model_validate(n) for n in notifications],
            size=len(notifications)
        )

    async def register_fcm_token(self, user_id: UUID, token: str) -> None:
        fcm_token = FCMToken(user_id=user_id, token=token)
        await self.repository.save_fcm_token(fcm_token)

    async def notify_order_confirmed(self, user_id: UUID, order_id: UUID) -> None:
        await self.repository.create(Notification(
            user_id=user_id,
            title="Orden confirmada",
            body="Tu orden fue confirmada exitosamente.",
            type="order_confirmed",
            reference_id=order_id,
        ))