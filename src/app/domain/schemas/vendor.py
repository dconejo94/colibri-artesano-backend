from pydantic import BaseModel
from uuid import UUID


class VendorProfileDTO(BaseModel):
    id: UUID
    name: str
    description: str | None
    product_count: int
