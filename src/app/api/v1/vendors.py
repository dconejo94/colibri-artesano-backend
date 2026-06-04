from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.services.store_service import StoreService
from app.api.deps import get_store_service
from app.domain.schemas.vendor import VendorProfileDTO
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/vendors", tags=["Vendors"])


@router.get("/{vendor_id}", response_model=VendorProfileDTO)
async def get_vendor_profile(
    vendor_id: UUID,
    service: StoreService = Depends(get_store_service),
):
    try:
        return await service.get_vendor_profile(vendor_id)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Vendor not found")
