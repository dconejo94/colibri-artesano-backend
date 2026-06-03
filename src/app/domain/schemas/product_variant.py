from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal


class ProductVariantCreateDTO(BaseModel):
    name: str
    value: str
    price_modifier: Decimal = Decimal("0")
    stock_quantity: int = 0


class ProductVariantUpdateDTO(BaseModel):
    name: str | None = None
    value: str | None = None
    price_modifier: Decimal | None = None
    stock_quantity: int | None = None


class ProductVariantResponseDTO(BaseModel):
    id: UUID
    product_id: UUID
    name: str
    value: str
    price_modifier: Decimal
    stock_quantity: int

    model_config = {"from_attributes": True}
