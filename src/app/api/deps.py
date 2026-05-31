from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

from app.infrastructure.category_repository_sqlalchemy import SQLAlchemyCategoryRepository
from app.infrastructure.store_repository_sqlalchemy import SQLAlchemyStoreRepository
from app.infrastructure.product_repository_sqlalchemy import SQLAlchemyProductRepository
from app.infrastructure.product_image_repository_sqlalchemy import SQLAlchemyProductImageRepository
from app.infrastructure.product_variant_repository_sqlalchemy import SQLAlchemyProductVariantRepository
from app.infrastructure.order_repository_sqlalchemy import SQLAlchemyOrderRepository

from app.services.category_service import CategoryService
from app.services.store_service import StoreService
from app.services.product_service import ProductService
from app.services.product_image_service import ProductImageService
from app.services.product_variant_service import ProductVariantService
from app.services.order_service import OrderService


async def get_category_service(
    db: AsyncSession = Depends(get_db),
) -> CategoryService:
    return CategoryService(SQLAlchemyCategoryRepository(db))


async def get_store_service(
    db: AsyncSession = Depends(get_db),
) -> StoreService:
    return StoreService(SQLAlchemyStoreRepository(db))


async def get_product_service(
    db: AsyncSession = Depends(get_db),
) -> ProductService:
    return ProductService(SQLAlchemyProductRepository(db))


async def get_product_image_service(
    db: AsyncSession = Depends(get_db),
) -> ProductImageService:
    return ProductImageService(SQLAlchemyProductImageRepository(db))


async def get_product_variant_service(
    db: AsyncSession = Depends(get_db),
) -> ProductVariantService:
    return ProductVariantService(SQLAlchemyProductVariantRepository(db))


async def get_order_service(
    db: AsyncSession = Depends(get_db),
) -> OrderService:
    return OrderService(
        order_repository=SQLAlchemyOrderRepository(db),
        product_repository=SQLAlchemyProductRepository(db),
    )
