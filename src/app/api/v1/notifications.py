from fastapi import APIRouter, Depends, Query

from app.core.security import CurrentUser

from app.domain.schemas.notification import (
    FCMTokenDTO,
    NotificationResponseDTO
)
from app.api.deps import get_notification_service
from app.services.notification_service import NotificationService
from app.domain.schemas.paginated_response import PaginatedResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/", response_model=PaginatedResponse[NotificationResponseDTO], status_code=200)
async def get_notifications(
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    service: NotificationService = Depends(get_notification_service)
):
    return await service.get_notifications(current_user.id, page, limit)

@router.post("/token", status_code=204)
async def register_fcm_token(
    dto: FCMTokenDTO,
    current_user: CurrentUser,
    service: NotificationService = Depends(get_notification_service)
):
    await service.register_fcm_token(current_user.id, dto.token)