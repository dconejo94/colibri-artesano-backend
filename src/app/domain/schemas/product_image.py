from pydantic import BaseModel
from uuid import UUID


class ProductImageCreateDTO(BaseModel):
    image_url: str
    is_primary: bool = False


class ProductImageResponseDTO(BaseModel):
    id: UUID
    product_id: UUID
    image_url: str
    is_primary: bool

    model_config = {"from_attributes": True}
