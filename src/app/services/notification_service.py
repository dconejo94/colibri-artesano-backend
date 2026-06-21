# app/services/notification_service.py
from uuid import UUID
from app.domain.models.notification import Notification
from app.domain.models.fcm_token import FCMToken
from app.domain.schemas.notification import NotificationResponseDTO
from app.repositories.notification_repository import NotificationRepository
from app.domain.schemas.paginated_response import PaginatedResponse


class NotificationService:
    def __init__(self, repository: NotificationRepository):
        self.repository = repository

    async def get_notifications(
        self,
        user_id: UUID,
        page: int,
        limit: int
    ) -> PaginatedResponse[NotificationResponseDTO]:

        notifications, total = await self.repository.get_by_user_id(
            user_id,
            page,
            limit
        )

        return PaginatedResponse(
            items=[
                NotificationResponseDTO.model_validate(n)
                for n in notifications
            ],
            page=page,
            limit=limit,
            total=total
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
    
    async def notify_new_product(
        self, user_ids: list[UUID], product_id: UUID, store_name: str, product_name: str
    ) -> None:
        for user_id in user_ids:
            await self.repository.create(Notification(
                user_id=user_id,
                title=f"Nuevo producto de {store_name}",
                body=f'{store_name} publicó "{product_name}"',
                type="new_product",
                reference_id=product_id,
            ))

    async def notify_new_event(
        self, user_ids: list[UUID], event_id: UUID, event_name: str
    ) -> None:
        for user_id in user_ids:
            await self.repository.create(Notification(
                user_id=user_id,
                title="Nuevo evento publicado",
                body=f'Nuevo "{event_name}"',
                type="new_event",
                reference_id=event_id,
            ))