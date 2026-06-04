import uuid

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
