from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.infrastructure.product_repository_sqlalchemy import SQLAlchemyProductRepository
from app.services.product_service import ProductService


async def get_product_service(
    db: AsyncSession = Depends(get_db),
):
    repository = SQLAlchemyProductRepository(db)
    return ProductService(repository)
