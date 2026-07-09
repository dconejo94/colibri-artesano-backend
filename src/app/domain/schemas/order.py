from pydantic import BaseModel
from typing import Literal
from uuid import UUID
from decimal import Decimal
from datetime import datetime

# The seller-facing status lifecycle a store order moves through.
SellerStatus = Literal["pending", "processing", "shipped", "delivered"]


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
    seller_status: SellerStatus


class MainOrderResponseDTO(BaseModel):
    id: UUID
    buyer_id: UUID
    total_amount: Decimal
    status: str
    payment_status: str = "pending"
    payment_method: str | None = None
    payment_reference: str | None = None
    created_at: datetime
    store_orders: list[StoreOrderResponseDTO] = []

    model_config = {"from_attributes": True}
