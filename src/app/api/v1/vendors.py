"""Legacy vendor profile endpoint — kept for backwards compatibility.

The ``GET /vendors/{store_id}`` route has been superseded by
``GET /stores/{store_id}/profile`` which correctly names the resource.
This file now only re-exports the router so that existing mobile clients
that still hit the old path continue to work during the transition period.

TODO: remove this file once the mobile app has migrated to the new path.
"""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.services.store_service import StoreService
from app.api.deps import get_store_service
from app.domain.schemas.vendor import VendorProfileDTO

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
    return await service.get_store_profile(store_id)
