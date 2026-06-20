import pytest
from fastapi import Depends, HTTPException
from sqlalchemy import event
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.core.database import get_db, Base
from app.core.rate_limit import limiter
from app.core.security import get_current_user
from app.infrastructure.user_repository_sqlalchemy import SQLAlchemyUserRepository

from tests.factories.product_factory import seed_products, TEST_USER_ID

# Rate limiting would make auth tests flaky; disable it for the whole suite.
limiter.enabled = False

# In-memory DB
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(engine.sync_engine, "connect")
def _enable_sqlite_fks(dbapi_connection, connection_record):
    """Enable FK enforcement in SQLite so cascade/FK bugs surface in tests."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestingSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


async def override_get_db():
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# Resolve auth to the seed user so existing tests need no token
async def override_get_current_user(db: AsyncSession = Depends(get_db)):
    user = await SQLAlchemyUserRepository(db).get_by_id(TEST_USER_ID)
    if user is None:
        raise HTTPException(status_code=401, detail="No authenticated user")
    return user


async def _make_client(*, override_auth: bool):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    app.dependency_overrides[get_db] = override_get_db
    if override_auth:
        from app.core.security import get_current_user_optional

        app.dependency_overrides[get_current_user] = override_get_current_user
        app.dependency_overrides[get_current_user_optional] = override_get_current_user

    async with TestingSessionLocal() as db:
        await seed_products(db)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=True,
    ) as c:
        yield c

    app.dependency_overrides.clear()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client():
    """Client where auth resolves to the seed user (no token needed)."""
    async for c in _make_client(override_auth=True):
        yield c


@pytest.fixture(scope="function")
async def auth_client():
    """Client exercising the real get_current_user (tokens required)."""
    async for c in _make_client(override_auth=False):
        yield c
