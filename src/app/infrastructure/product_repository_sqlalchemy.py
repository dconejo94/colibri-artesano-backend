from sqlalchemy.orm import Session

from app.domain.models.product import Product
from app.repositories.product_repository import ProductRepository


class SQLAlchemyProductRepository(ProductRepository):
    def __init__(self, db: Session):
        self.db = db

    def list_products(self, page: int, limit: int, category: str | None = None):
        query = self.db.query(Product)

        if category:
            query = query.filter(Product.category == category)

        total = query.count()

        items = query.offset((page - 1) * limit).limit(limit).all()

        return items, total

    def get_product_by_id(self, id: int):
        return self.db.query(Product).filter(Product.id == id).first()
