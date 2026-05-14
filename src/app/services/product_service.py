class ProductService:
    def __init__(self, repository):
        self.repository = repository

    def get_all_products(self, page: int, limit: int, category: str | None = None):
        return self.repository.list_products(page=page, limit=limit, category=category)
