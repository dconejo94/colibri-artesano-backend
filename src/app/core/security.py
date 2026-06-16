import uuid
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

# Matches Daniel's user in seed.sql (a0eebc99-...) who owns store 10000000-...0001.
# TEMPORAL: replace with real JWT extraction once auth is implemented.
_SEED_USER_ID = uuid.UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11")


# TEMPORAL: devuelve el usuario fijo del seed mientras la autenticación real esté pendiente.
async def get_current_user(db: AsyncSession = Depends(get_db)):
    from app.infrastructure.user_repository_sqlalchemy import SQLAlchemyUserRepository

    repo = SQLAlchemyUserRepository(db)
    user = await repo.get_by_id(_SEED_USER_ID)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authenticated user",
        )
    return user


# TEMPORAL: stub de RBAC — valida role=='vendor' hasta que llegue auth real.
async def require_vendor_role(user=Depends(get_current_user)):
    if user.role != "vendor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vendor role required",
        )
    return user


async def require_store_owner(
    store_id: UUID,
    user=Depends(require_vendor_role),
    db: AsyncSession = Depends(get_db),
):
    """Validates that the authenticated vendor owns the requested store.

    Prevents horizontal privilege escalation (IDOR): a vendor with a valid
    role token must not be able to mutate another vendor's store or products.

    TEMPORAL: when real JWT auth replaces get_current_user, this function
    does not need to change — it already compares store.owner_id == user.id
    and will work with any real User object returned by the auth layer.
    """
    from app.infrastructure.store_repository_sqlalchemy import SQLAlchemyStoreRepository

    repo = SQLAlchemyStoreRepository(db)
    store = await repo.get_by_id(store_id)
    if store is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Store not found"
        )
    if store.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this store",
        )
    return user


async def require_product_owner(
    product_id: UUID,
    user=Depends(require_vendor_role),
    db: AsyncSession = Depends(get_db),
):
    """Validates that the authenticated vendor owns the store that contains
    the requested product.

    Traversal: product → product.store_id → store.owner_id == user.id.

    Applied to: PUT/DELETE /products/{id}, and all
    /{product_id}/images and /{product_id}/variants mutation endpoints.

    TEMPORAL: same note as require_store_owner — no changes needed here when
    real JWT auth lands.
    """
    from app.infrastructure.product_repository_sqlalchemy import (
        SQLAlchemyProductRepository,
    )
    from app.infrastructure.store_repository_sqlalchemy import SQLAlchemyStoreRepository

    product_repo = SQLAlchemyProductRepository(db)
    product = await product_repo.get_by_id(product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    store_repo = SQLAlchemyStoreRepository(db)
    store = await store_repo.get_by_id(product.store_id)
    if store is None or store.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this product",
        )
    return user
