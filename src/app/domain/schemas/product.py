from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal
from datetime import datetime

from app.domain.schemas.product_image import ProductImageResponseDTO
from app.domain.schemas.product_variant import ProductVariantResponseDTO
from app.domain.schemas.store import StoreResponseDTO
from app.domain.schemas.category import CategoryResponseDTO


class ProductCreateDTO(BaseModel):
    category_id: UUID
    name: str
    description: str | None = None
    base_price: Decimal
    is_active: bool = True


class ProductUpdateDTO(BaseModel):
    category_id: UUID | None = None
    name: str | None = None
    description: str | None = None
    base_price: Decimal | None = None
    is_active: bool | None = None


class ProductResponseDTO(BaseModel):
    id: UUID
    store_id: UUID
    category_id: UUID | None
    name: str
    description: str | None
    base_price: Decimal
    is_active: bool
    created_at: datetime
    
    store: StoreResponseDTO | None = None
    category: CategoryResponseDTO | None = None
    images: list[ProductImageResponseDTO] = []
    variants: list[ProductVariantResponseDTO] = []

    model_config = {"from_attributes": True}


class ProductDetailResponseDTO(ProductResponseDTO):
    pass
