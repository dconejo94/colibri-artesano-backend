import uuid
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

_SEED_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


# TEMPORAL: devuelve el usuario fijo del seed (id=00000000-0000-0000-0000-000000000001) en lo que estan los issues de autenticacion de Fabian.
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


# TEMPORAL: stub de RBAC mientras el issue de auth de Fabian este pendiente.
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

    TODO(auth/Fabian): once real JWT auth lands, replace the ``_SEED_USER_ID``
    stub in ``get_current_user`` with the actual token payload.  The ownership
    check here does NOT need to change — it already compares
    ``store.owner_id == user.id`` which will work with a real user object.
    See: https://github.com/<org>/colibri-artesano/issues/<fabian-auth-issue>
    """
    from app.infrastructure.store_repository_sqlalchemy import SQLAlchemyStoreRepository

    repo = SQLAlchemyStoreRepository(db)
    store = await repo.get_by_id(store_id)
    if store is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store not found")
    if store.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this store",
        )
    return user

