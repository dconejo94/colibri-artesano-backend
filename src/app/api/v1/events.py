from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException

from app.services.event_service import EventService
from app.api.deps import get_event_service
from app.domain.schemas.event import (
    EventCreateDTO,
    EventUpdateDTO,
    EventResponseDTO,
    ParticipantReviewDTO,
    ParticipantResponseDTO,
)
from app.domain.schemas.paginated_response import PaginatedResponse
from app.core.exceptions import NotFoundException, ConflictException, ForbiddenException
from app.core.security import CurrentUser

router = APIRouter(prefix="/events", tags=["Events"])


def require_admin(current_user: CurrentUser) -> CurrentUser:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin role required")
    return current_user


# ── Events read ───────────────────────────────────────────────────


@router.get("/", response_model=PaginatedResponse[EventResponseDTO])
async def list_events(
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    service: EventService = Depends(get_event_service),
):
    store_id = current_user.store.id if current_user.store else None
    return await service.list_events(
        page=page,
        limit=limit,
        user_role=current_user.role,
        user_store_id=store_id,
    )


@router.get("/{event_id}", response_model=EventResponseDTO)
async def get_event(
    event_id: UUID,
    current_user: CurrentUser,
    service: EventService = Depends(get_event_service),
):
    store_id = current_user.store.id if current_user.store else None
    try:
        return await service.get_event(
            event_id,
            user_role=current_user.role,
            user_store_id=store_id,
        )
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Event not found")

@router.get("/list_upcoming", response_model=PaginatedResponse[EventResponseDTO])
async def list_upcoming(
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    service: EventService = Depends(get_event_service),
):
    store_id = current_user.store.id if current_user.store else None
    return await service.list_upcoming(page, limit, current_user.role, store_id)

@router.get("/list_nearby", response_model=PaginatedResponse[EventResponseDTO])
async def list_nearby(
    current_user: CurrentUser,
    lat: float,
    lng: float,
    radius_km: float,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    service: EventService = Depends(get_event_service),
):
    store_id = current_user.store.id if current_user.store else None
    return await service.list_nearby(lat, lng, radius_km, page, limit, current_user.role, store_id)

# ── Events write (admin only) ─────────────────────────────────────


@router.post("/", response_model=EventResponseDTO, status_code=201)
async def create_event(
    dto: EventCreateDTO,
    current_user: CurrentUser,
    service: EventService = Depends(get_event_service),
):
    require_admin(current_user)
    return await service.create_event(creator_id=current_user.id, dto=dto)


@router.patch("/{event_id}", response_model=EventResponseDTO)
async def update_event(
    event_id: UUID,
    dto: EventUpdateDTO,
    current_user: CurrentUser,
    service: EventService = Depends(get_event_service),
):
    require_admin(current_user)
    try:
        return await service.update_event(event_id, dto)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Event not found")


@router.delete("/{event_id}", status_code=204)
async def delete_event(
    event_id: UUID,
    current_user: CurrentUser,
    service: EventService = Depends(get_event_service),
):
    require_admin(current_user)
    try:
        await service.delete_event(event_id)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Event not found")


# ── Participants ──────────────────────────────────────────────────


@router.post(
    "/{event_id}/participants", response_model=ParticipantResponseDTO, status_code=201
)
async def request_participation(
    event_id: UUID,
    current_user: CurrentUser,
    service: EventService = Depends(get_event_service),
):
    if current_user.role != "vendor":
        raise HTTPException(status_code=403, detail="Vendor role required")
    if current_user.store is None:
        raise HTTPException(status_code=400, detail="You do not have a store")
    try:
        return await service.request_participation(
            event_id=event_id,
            store_id=current_user.store.id,
            requested_by=current_user.id,
        )
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Event not found")
    except ConflictException as e:
        raise HTTPException(status_code=409, detail=e.detail)


@router.delete("/{event_id}/participants/{store_id}", status_code=204)
async def withdraw_participation(
    event_id: UUID,
    store_id: UUID,
    current_user: CurrentUser,
    service: EventService = Depends(get_event_service),
):
    if current_user.role != "vendor":
        raise HTTPException(status_code=403, detail="Vendor role required")
    try:
        await service.withdraw_participation(
            event_id=event_id,
            store_id=store_id,
            user_id=current_user.id,
        )
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Participation not found")
    except ForbiddenException as e:
        raise HTTPException(status_code=403, detail=e.detail)


@router.get("/{event_id}/participants", response_model=list[ParticipantResponseDTO])
async def list_participants(
    event_id: UUID,
    current_user: CurrentUser,
    service: EventService = Depends(get_event_service),
):
    require_admin(current_user)
    try:
        return await service.list_participants(event_id)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Event not found")


@router.patch(
    "/{event_id}/participants/{store_id}", response_model=ParticipantResponseDTO
)
async def review_participation(
    event_id: UUID,
    store_id: UUID,
    dto: ParticipantReviewDTO,
    current_user: CurrentUser,
    service: EventService = Depends(get_event_service),
):
    require_admin(current_user)
    try:
        return await service.review_participation(
            event_id=event_id,
            store_id=store_id,
            reviewed_by=current_user.id,
            dto=dto,
        )
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Participation not found")
