from fastapi import APIRouter, Depends, Query, HTTPException

from app.core.security import CurrentUser

from app.domain.schemas.notification import (
    FCMTokenDTO,
    NotificationListResponseDTO
)
from app.core.exceptions import NotFoundException, ConflictException
from app.api.deps import get_notification_service
from app.services.notification_service import NotificationService


router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/", response_model=NotificationListResponseDTO, status_code=200)
async def get_notifications(
    current_user: CurrentUser,
    service: NotificationService = Depends(get_notification_service)
):
    return await service.get_notifications(current_user.id)

@router.post("/token", status_code=204)
async def register_fcm_token(
    dto: FCMTokenDTO,
    current_user: CurrentUser,
    service: NotificationService = Depends(get_notification_service)
):
    await service.register_fcm_token(current_user.id, dto.token)