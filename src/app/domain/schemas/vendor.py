from pydantic import BaseModel
from uuid import UUID


class StoreProfileDTO(BaseModel):
    id: UUID
    name: str
    description: str | None
    product_count: int
    follower_count: int
    is_following: bool = False


# Backwards-compatible alias used by the deprecated GET /vendors/{store_id} route.
VendorProfileDTO = StoreProfileDTO
