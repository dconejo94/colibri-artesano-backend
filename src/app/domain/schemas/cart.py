from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel


class CartItemResponseDTO(BaseModel):
    id: UUID

    product_id: UUID
    product_name: str
    product_image_url: str | None = None

    variant_id: UUID | None = None
    variant_name: str | None = None
    variant_value: str | None = None

    quantity: int

    unit_price: Decimal
    subtotal: Decimal

    model_config = {"from_attributes": True}


class CartStoreResponseDTO(BaseModel):
    store_id: UUID
    store_name: str

    subtotal_amount: Decimal

    items: list[CartItemResponseDTO]

    model_config = {"from_attributes": True}


class CartResponseDTO(BaseModel):
    order_id: UUID | None
    buyer_id: UUID

    total_amount: Decimal

    stores: list[CartStoreResponseDTO]

    model_config = {"from_attributes": True}
