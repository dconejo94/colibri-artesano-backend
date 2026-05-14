from app.domain.schemas.paginated_response import PaginatedProductsResponseDTO


class ProductService:
    def __init__(self, repository):
        self.repository = repository

    def get_all_products(self, page: int, limit: int, category: str | None = None):
        items, total = self.repository.list_products(page, limit, category)
        return PaginatedProductsResponseDTO(
            items=items, page=page, limit=limit, total=total
        )
