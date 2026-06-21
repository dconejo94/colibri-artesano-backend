# app/repositories/notification_repository.py
from abc import ABC, abstractmethod
from uuid import UUID
from app.domain.models.notification import Notification
from app.domain.models.fcm_token import FCMToken


class NotificationRepository(ABC):
    @abstractmethod
    async def get_by_user_id(
        self, user_id: UUID, page: int, limit: int
    ) -> tuple[list[Notification], int]:
        pass

    @abstractmethod
    async def get_unread_by_user_id(
        self, user_id: UUID, page: int, limit: int
    ) -> tuple[list[Notification], int]:
        pass

    @abstractmethod
    async def create(self, notification: Notification) -> Notification:
        pass

    @abstractmethod
    async def save_fcm_token(self, fcm_token: FCMToken) -> FCMToken:
        pass

    @abstractmethod
    async def get_fcm_tokens_by_user(self, user_id: UUID) -> list[FCMToken]:
        pass

    @abstractmethod
    async def get_notification_by_id(
        self, notification_id: UUID
    ) -> Notification | None:
        pass

    @abstractmethod
    async def update(self, notification: Notification) -> None:
        pass
