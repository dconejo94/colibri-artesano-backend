"""Password hashing, JWT token utilities and the authentication dependency."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import UUID

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.database import get_db
from app.domain.models.user import User

logger = logging.getLogger(__name__)

# bcrypt>=4 rejects input over 72 bytes; cap it so long passwords don't 500.
_BCRYPT_MAX_BYTES = 72

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"

# Reads the bearer token from the Authorization header (tokenUrl is docs-only).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


class TokenError(Exception):
    """Raised when a JWT is missing, malformed, expired or of the wrong type."""


# Password hasshing


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password with bcrypt (salted, slow by design)."""
    password_bytes = plain_password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Return True if the plaintext password matches the stored hash."""
    password_bytes = plain_password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    try:
        return bcrypt.checkpw(password_bytes, password_hash.encode("utf-8"))
    except ValueError:
        # Malformed or empty stored hash: treat as a non-match.
        return False


# JWT tokens


def _create_token(user_id: UUID, token_type: str, expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def create_access_token(user_id: UUID) -> str:
    """Create a short-lived access token for the given user."""
    return _create_token(
        user_id,
        ACCESS_TOKEN_TYPE,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(user_id: UUID) -> str:
    """Create a long-lived refresh token for the given user."""
    return _create_token(
        user_id,
        REFRESH_TOKEN_TYPE,
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str, *, expected_type: str) -> UUID:
    """Verify a token's signature, expiry and type, returning its user id.

    Raises:
        TokenError: if the token is expired, malformed, or not of
            ``expected_type``.
    """
    try:
        claims = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.ExpiredSignatureError:
        raise TokenError("Token has expired") from None
    except jwt.PyJWTError as exc:
        logger.debug("JWT validation failed: %s", exc)
        raise TokenError("Invalid token") from None

    if claims.get("type") != expected_type:
        raise TokenError(f"Expected a {expected_type} token")

    subject = claims.get("sub")
    try:
        return UUID(subject)
    except (ValueError, TypeError):
        raise TokenError("Invalid subject in token") from None


# Authentication dependency


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Resolve the authenticated user from a Bearer access token."""
    from app.infrastructure.user_repository_sqlalchemy import SQLAlchemyUserRepository

    try:
        user_id = decode_token(token, expected_type=ACCESS_TOKEN_TYPE)
    except TokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    user = await SQLAlchemyUserRepository(db).get_by_id(user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# Convenient alias for route signatures: `user: CurrentUser`.
CurrentUser = Annotated[User, Depends(get_current_user)]


async def require_vendor_role(user: CurrentUser) -> User:
    """Require the authenticated user to have the vendor role."""
    if user.role != "vendor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vendor role required",
        )
    return user


async def require_vendor_or_admin(user: CurrentUser) -> User:
    """Require the authenticated user to be a vendor or platform admin."""
    if user.role != "vendor" and not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vendor or admin role required",
        )
    return user


async def require_store_owner(
    store_id: UUID,
    user: User = Depends(require_vendor_role),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Require the authenticated vendor to own the requested store (prevents IDOR)."""
    from app.infrastructure.store_repository_sqlalchemy import SQLAlchemyStoreRepository

    store = await SQLAlchemyStoreRepository(db).get_by_id(store_id)
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
    user: User = Depends(require_vendor_role),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Require the authenticated vendor to own the store containing the product."""
    from app.infrastructure.product_repository_sqlalchemy import (
        SQLAlchemyProductRepository,
    )
    from app.infrastructure.store_repository_sqlalchemy import SQLAlchemyStoreRepository

    product = await SQLAlchemyProductRepository(db).get_by_id(product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    store = await SQLAlchemyStoreRepository(db).get_by_id(product.store_id)
    if store is None or store.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this product",
        )
    return user
