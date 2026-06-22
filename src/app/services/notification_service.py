# app/services/notification_service.py
from uuid import UUID
from app.domain.models.notification import Notification
from app.domain.schemas.notification import NotificationResponseDTO, FCMTokenDTO
from app.repositories.notification_repository import NotificationRepository
from app.domain.schemas.paginated_response import PaginatedResponse

from app.core.exceptions import NotFoundException


class NotificationService:
    def __init__(self, repository: NotificationRepository):
        self.repository = repository

    async def get_notifications(
        self, user_id: UUID, page: int, limit: int
    ) -> PaginatedResponse[NotificationResponseDTO]:

        notifications, total = await self.repository.get_by_user_id(
            user_id, page, limit
        )

        return await self._build_paginated_response(notifications, total, page, limit)

    async def get_notifications_unread(
        self, user_id: UUID, page: int, limit: int
    ) -> PaginatedResponse[NotificationResponseDTO]:

        notifications, total = await self.repository.get_unread_by_user_id(
            user_id, page, limit
        )

        return await self._build_paginated_response(notifications, total, page, limit)

    async def register_fcm_token(self, user_id: UUID, token: str) -> None:
        await self.repository.save_fcm_token(user_id=user_id, token=token)

    async def mark_notification_as_read(
        self, user_id: UUID, notification_id: UUID
    ) -> None:
        notification = await self.repository.get_notification_by_id(notification_id)
        if notification is None:
            raise NotFoundException("Notification", str(notification_id))
        if notification.user_id != user_id:
            raise NotFoundException("Notification", str(notification_id))
        notification.is_read = True
        await self.repository.update(notification)

    async def notify_order_confirmed(self, user_id: UUID, order_id: UUID) -> None:
        await self.repository.create(
            Notification(
                user_id=user_id,
                title="Orden confirmada",
                body="Tu orden fue confirmada exitosamente.",
                type="order_confirmed",
                reference_id=order_id,
            )
        )

    async def get_user_notification_tokens(self, user_id: UUID) -> list[FCMTokenDTO]:
        tokens = await self.repository.get_fcm_tokens_by_user(user_id)
        return [FCMTokenDTO.model_validate(token) for token in tokens]

    async def notify_new_product(
        self, user_ids: list[UUID], product_id: UUID, store_name: str, product_name: str
    ) -> None:
        for user_id in user_ids:
            await self.repository.create(
                Notification(
                    user_id=user_id,
                    title=f"Nuevo producto de {store_name}",
                    body=f'{store_name} publicó "{product_name}"',
                    type="new_product",
                    reference_id=product_id,
                )
            )

    async def _build_paginated_response(
        self, notifications: list[Notification], total: int, page: int, limit: int
    ) -> PaginatedResponse[NotificationResponseDTO]:
        return PaginatedResponse(
            items=[NotificationResponseDTO.model_validate(n) for n in notifications],
            page=page,
            limit=limit,
            total=total,
        )
