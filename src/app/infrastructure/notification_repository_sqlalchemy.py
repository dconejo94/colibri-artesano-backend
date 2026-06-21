# app/infrastructure/sqlalchemy_notification_repository.py
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession


from app.domain.models.notification import Notification
from app.domain.models.fcm_token import FCMToken
from app.repositories.notification_repository import NotificationRepository

class SQLAlchemyNotificationRepository(NotificationRepository):
    def __init__(self, db: AsyncSession):
        self.db = db


    async def get_by_user_id(
        self,
        user_id: UUID,
        page: int,
        limit: int
    ) -> tuple[list[Notification], int]:

        total = await self.db.scalar(
            select(func.count())
            .select_from(Notification)
            .where(Notification.user_id == user_id)
        )

        result = await self.db.execute(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )

        return list(result.scalars().all()), total or 0

    async def get_unread_by_user_id(
        self,
        user_id: UUID,
        page: int,
        limit: int
    ) -> tuple[list[Notification], int]:

        total = await self.db.scalar(
            select(func.count())
            .select_from(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        )

        result = await self.db.execute(
            select(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
            .order_by(Notification.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )

        return list(result.scalars().all()), total or 0

    async def create(self, notification: Notification) -> Notification:
        self.db.add(notification)
        await self.db.flush()
        await self.db.refresh(notification)
        return notification

    async def save_fcm_token(self, fcm_token: FCMToken) -> FCMToken:
        existing = await self.db.execute(
            select(FCMToken).where(FCMToken.token == fcm_token.token)
        )
        existing = existing.scalars().first()

        if existing:
            existing.user_id = fcm_token.user_id
            await self.db.flush()
            return existing

        self.db.add(fcm_token)
        await self.db.flush()
        await self.db.refresh(fcm_token)
        return fcm_token

    async def get_fcm_tokens_by_user(self, user_id: UUID) -> list[FCMToken]:
        result = await self.db.execute(
            select(FCMToken).where(FCMToken.user_id == user_id)
        )
        return list(result.scalars().all())