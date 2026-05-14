from pydantic import BaseModel

from app.domain.schemas.product import ProductResponseDTO


class PaginatedProductsResponseDTO(BaseModel):
    items: list[ProductResponseDTO]
    page: int
    limit: int
    total: int
