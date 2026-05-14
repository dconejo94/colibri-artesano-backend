from pydantic import BaseModel

from decimal import Decimal


class ProductResponseDTO(BaseModel):
    id: int
    name: str
    description: str | None
    price: Decimal
    stock: int
    image_url: str | None
    category: str | None

    model_config = {"from_attributes": True}
