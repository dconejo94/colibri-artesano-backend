from pydantic import BaseModel


class ProductResponseDTO(BaseModel):
    id: int
    name: str
    description: str | None
    price: float
    stock: int
    image_url: str | None
    category: str | None

    model_config = {"from_attributes": True}
