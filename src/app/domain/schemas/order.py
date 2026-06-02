from pydantic import BaseModel, Field
from uuid import UUID
from decimal import Decimal
from datetime import datetime


class OrderItemCreateDTO(BaseModel):
    product_id: UUID
    variant_id: UUID | None = None
    quantity: int = Field(..., gt=0)


class OrderItemResponseDTO(BaseModel):
    id: UUID
    store_order_id: UUID
    product_id: UUID
    variant_id: UUID | None
    quantity: int
    unit_price: Decimal

    model_config = {"from_attributes": True}


class StoreOrderResponseDTO(BaseModel):
    id: UUID
    main_order_id: UUID
    store_id: UUID
    seller_status: str
    subtotal_amount: Decimal
    created_at: datetime
    items: list[OrderItemResponseDTO] = []

    model_config = {"from_attributes": True}


class StoreOrderStatusUpdateDTO(BaseModel):
    seller_status: str


class MainOrderCreateDTO(BaseModel):
    buyer_id: UUID
    items: list[OrderItemCreateDTO] = Field(..., min_length=1)


class MainOrderResponseDTO(BaseModel):
    id: UUID
    buyer_id: UUID
    total_amount: Decimal
    status: str
    created_at: datetime
    store_orders: list[StoreOrderResponseDTO] = []

    model_config = {"from_attributes": True}
