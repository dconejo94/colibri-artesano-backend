"""Legacy vendor profile endpoint — kept for backwards compatibility.

The ``GET /vendors/{store_id}`` route has been superseded by
``GET /stores/{store_id}/profile`` which correctly names the resource.
This file now only re-exports the router so that existing mobile clients
that still hit the old path continue to work during the transition period.

TODO: remove this file once the mobile app has migrated to the new path.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.services.store_service import StoreService
from app.api.deps import get_store_service
from app.domain.schemas.vendor import VendorProfileDTO
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/vendors", tags=["Vendors (deprecated)"])


@router.get(
    "/{store_id}",
    response_model=VendorProfileDTO,
    deprecated=True,
    description="Deprecated. Use `GET /stores/{store_id}/profile` instead.",
)
async def get_vendor_profile_legacy(
    store_id: UUID,
    service: StoreService = Depends(get_store_service),
):
    try:
        return await service.get_vendor_profile(store_id)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Store not found")

