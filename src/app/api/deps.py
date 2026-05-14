from fastapi import Depends
from sqlalchemy.orm import Session


from app.core.database import get_db
from app.infrastructure.product_repository_sqlalchemy import SQLAlchemyProductRepository
from app.services.product_service import ProductService


def get_product_service(
    db: Session = Depends(get_db),
):
    repository = SQLAlchemyProductRepository(db)
    return ProductService(repository)
