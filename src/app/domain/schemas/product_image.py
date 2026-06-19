from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


class ProductImageCreateDTO(BaseModel):
    image_url: str
    is_primary: bool = False


class ProductImageUploadRequestDTO(BaseModel):
    filename: str
    content_type: str


class ProductImageUploadResponseDTO(BaseModel):
    upload_url: str
    blob_url: str
    expires_at: datetime


class ProductImageResponseDTO(BaseModel):
    id: UUID
    product_id: UUID
    image_url: str
    is_primary: bool

    model_config = {"from_attributes": True}
