from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException

from app.services.event_service import EventService
from app.api.deps import get_event_service
from app.domain.schemas.event import EventCreateDTO, EventResponseDTO
from app.domain.schemas.paginated_response import PaginatedResponse
from app.core.exceptions import NotFoundException
from app.core.security import CurrentUser, require_vendor_or_admin

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("/", response_model=PaginatedResponse[EventResponseDTO])
async def list_events(
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    service: EventService = Depends(get_event_service),
):
    return await service.list_events(page=page, limit=limit)


@router.post("/", response_model=EventResponseDTO, status_code=201)
async def create_event(
    dto: EventCreateDTO,
    current_user: CurrentUser,
    _: object = Depends(require_vendor_or_admin),
    service: EventService = Depends(get_event_service),
):
    return await service.create_event(creator_id=current_user.id, dto=dto)


@router.get("/{event_id}", response_model=EventResponseDTO)
async def get_event(
    event_id: UUID,
    current_user: CurrentUser,
    service: EventService = Depends(get_event_service),
):
    try:
        return await service.get_event(event_id)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Event not found")
