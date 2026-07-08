import uuid
import pytest
from fastapi import Depends, HTTPException, Request
from sqlalchemy import event
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.core.database import get_db, Base
from app.core.rate_limit import limiter
from app.core.security import get_current_user, get_current_user_optional
from app.infrastructure.user_repository_sqlalchemy import SQLAlchemyUserRepository

from tests.factories.product_factory import seed_products, TEST_USER_ID, TEST_USER_ID2

limiter.enabled = False

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(engine.sync_engine, "connect")
def _enable_sqlite_fks(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def override_get_db():
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def override_get_current_user_by_header(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user_id_str = request.headers.get("X-Test-User-Id", str(TEST_USER_ID))
    user_id = uuid.UUID(user_id_str)
    user = await SQLAlchemyUserRepository(db).get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="No authenticated user")
    return user


async def _make_client(*, override_auth: bool, default_headers: dict | None = None):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    app.dependency_overrides[get_db] = override_get_db

    if override_auth:
        app.dependency_overrides[get_current_user] = override_get_current_user_by_header
        app.dependency_overrides[get_current_user_optional] = (
            override_get_current_user_by_header
        )

    async with TestingSessionLocal() as db:
        await seed_products(db)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=True,
        headers=default_headers or {},
    ) as c:
        yield c

    app.dependency_overrides.clear()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client():
    async for c in _make_client(override_auth=True):
        yield c


@pytest.fixture(scope="function")
async def follower_client(client):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=True,
        headers={"X-Test-User-Id": str(TEST_USER_ID2)},
    ) as c:
        yield c


@pytest.fixture(scope="function")
async def auth_client():
    async for c in _make_client(override_auth=False):
        yield c
