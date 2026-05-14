from app.domain.schemas.paginated_response import PaginatedProductsResponseDTO
from app.core.exceptions import ProductNotFoundException
from app.repositories.product_repository import ProductRepository


class ProductService:
    def __init__(self, repository: ProductRepository):
        self.repository = repository

    def get_all_products(self, page: int, limit: int, category: str | None = None):
        items, total = self.repository.list_products(page, limit, category)
        return PaginatedProductsResponseDTO(
            items=items, page=page, limit=limit, total=total
        )

    def get_product_by_id(self, id: int):
        product = self.repository.get_product_by_id(id=id)

        if not product:
            raise ProductNotFoundException()

        return product
