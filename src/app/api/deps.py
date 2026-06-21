from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

from app.infrastructure.user_repository_sqlalchemy import SQLAlchemyUserRepository
from app.infrastructure.category_repository_sqlalchemy import (
    SQLAlchemyCategoryRepository,
)
from app.infrastructure.store_repository_sqlalchemy import SQLAlchemyStoreRepository
from app.infrastructure.product_repository_sqlalchemy import SQLAlchemyProductRepository
from app.infrastructure.product_image_repository_sqlalchemy import (
    SQLAlchemyProductImageRepository,
)
from app.infrastructure.product_variant_repository_sqlalchemy import (
    SQLAlchemyProductVariantRepository,
)
from app.infrastructure.order_repository_sqlalchemy import SQLAlchemyOrderRepository
from app.infrastructure.search_repository_sqlalchemy import (
    SQLAlchemyProductSearchRepository,
)
from app.infrastructure.event_repository_sqlalchemy import SQLAlchemyEventRepository
from app.infrastructure.cart_repository_sqlalchemy import SQLAlchemyCartRepository

from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.category_service import CategoryService
from app.services.store_service import StoreService
from app.services.product_service import ProductService
from app.services.product_image_service import ProductImageService
from app.services.product_variant_service import ProductVariantService
from app.services.order_service import OrderService
from app.services.search_service import SearchService
from app.services.event_service import EventService
from app.services.cart_service import CartService
from app.services.store_order_service import StoreOrderService

from app.config import settings
from app.infrastructure.azure_blob_storage import BlobStorageService


async def get_auth_service(
    db: AsyncSession = Depends(get_db),
) -> AuthService:
    return AuthService(
        user_repository=SQLAlchemyUserRepository(db),
        store_repository=SQLAlchemyStoreRepository(db),
    )


async def get_user_service(
    db: AsyncSession = Depends(get_db),
) -> UserService:
    return UserService(SQLAlchemyUserRepository(db))


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
    return ProductService(
        repository=SQLAlchemyProductRepository(db),
        category_repository=SQLAlchemyCategoryRepository(db),
        variant_repository=SQLAlchemyProductVariantRepository(db),
    )


def get_blob_storage_service() -> BlobStorageService:
    return BlobStorageService(
        account_name=settings.AZURE_STORAGE_ACCOUNT_NAME,
        account_key=settings.AZURE_STORAGE_ACCOUNT_KEY,
        container=settings.AZURE_STORAGE_CONTAINER,
        base_url=settings.AZURE_BLOB_BASE_URL,
        sas_expiry_minutes=settings.AZURE_STORAGE_SAS_EXPIRY_MINUTES,
    )


async def get_product_image_service(
    db: AsyncSession = Depends(get_db),
    blob_storage: BlobStorageService = Depends(get_blob_storage_service),
) -> ProductImageService:
    return ProductImageService(
        SQLAlchemyProductImageRepository(db),
        blob_storage=blob_storage,
        validate_image_url=settings.AZURE_STORAGE_VALIDATE_IMAGE_URL,
    )


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
        variant_repository=SQLAlchemyProductVariantRepository(db),
    )


async def get_search_service(
    db: AsyncSession = Depends(get_db),
) -> SearchService:
    return SearchService(SQLAlchemyProductSearchRepository(db))


async def get_event_service(
    db: AsyncSession = Depends(get_db),
) -> EventService:
    return EventService(SQLAlchemyEventRepository(db))
async def get_cart_service(
    db: AsyncSession = Depends(get_db),
) -> CartService:
    cart_repository = SQLAlchemyCartRepository(db)
    store_order_service = StoreOrderService(
        cart_repository=cart_repository,
        variant_repository=SQLAlchemyProductVariantRepository(db),
    )
    return CartService(
        cart_repository=cart_repository,
        order_repository=SQLAlchemyOrderRepository(db),
        product_repository=SQLAlchemyProductRepository(db),
        store_order_service=store_order_service,
    )
