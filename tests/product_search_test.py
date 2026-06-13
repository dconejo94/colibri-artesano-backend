"""Tests for GET /api/v1/products/search and GET /api/v1/products/autocomplete.

The test database is SQLite (aiosqlite).  Search uses ILIKE which degrades
gracefully to case-insensitive LIKE on SQLite, so the same test suite covers
the repository logic without requiring a live PostgreSQL instance.

Seed data (provided by the overridden ``client`` fixture below):
  - "Huipil Bordado"        — active, category: Textiles
  - "Collar de Jade"        — active, category: Joyería
  - "Tapete de Palma"       — active, category: Textiles
  - "Vasija de Barro"       — inactive (is_active=False)
  - "Bolsa de Cuero"        — active, no description
"""

import uuid
from decimal import Decimal

import pytest
from httpx import AsyncClient, ASGITransport

from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.main import app
from app.core.database import get_db, Base
from app.domain.models.user import User
from app.domain.models.store import Store
from app.domain.models.category import Category
from app.domain.models.product import Product

# ---------------------------------------------------------------------------
# Test database setup
# ---------------------------------------------------------------------------

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test_search.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)


@event.listens_for(engine.sync_engine, "connect")
def _enable_sqlite_fks(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# Fixed UUIDs for deterministic assertions
_USER_ID = uuid.UUID("aaaaaaaa-0000-0000-0000-000000000001")
_STORE_ID = uuid.UUID("aaaaaaaa-0000-0000-0000-000000000002")
_CAT_TEXTILES = uuid.UUID("aaaaaaaa-0000-0000-0000-000000000003")
_CAT_JOYERIA = uuid.UUID("aaaaaaaa-0000-0000-0000-000000000004")
_PROD_HUIPIL = uuid.UUID("aaaaaaaa-0000-0000-0000-000000000010")
_PROD_COLLAR = uuid.UUID("aaaaaaaa-0000-0000-0000-000000000011")
_PROD_TAPETE = uuid.UUID("aaaaaaaa-0000-0000-0000-000000000012")
_PROD_VASIJA = uuid.UUID("aaaaaaaa-0000-0000-0000-000000000013")  # inactive
_PROD_BOLSA = uuid.UUID("aaaaaaaa-0000-0000-0000-000000000014")


async def _seed(db) -> None:
    """Insert deterministic test data into the search test database."""
    user = User(
        id=_USER_ID, email="search@test.com", password_hash="hash", role="vendor"
    )
    db.add(user)

    store = Store(id=_STORE_ID, owner_id=_USER_ID, name="Search Test Store")
    db.add(store)

    cat_textiles = Category(id=_CAT_TEXTILES, name="Textiles", slug="textiles")
    cat_joyeria = Category(id=_CAT_JOYERIA, name="Joyería", slug="joyeria")
    db.add(cat_textiles)
    db.add(cat_joyeria)

    products = [
        Product(
            id=_PROD_HUIPIL,
            store_id=_STORE_ID,
            category_id=_CAT_TEXTILES,
            name="Huipil Bordado",
            description="Huipil tradicional con bordado a mano en hilos de colores",
            base_price=Decimal("350.00"),
            is_active=True,
        ),
        Product(
            id=_PROD_COLLAR,
            store_id=_STORE_ID,
            category_id=_CAT_JOYERIA,
            name="Collar de Jade",
            description="Collar artesanal elaborado con piedras de jade guatemalteco",
            base_price=Decimal("280.00"),
            is_active=True,
        ),
        Product(
            id=_PROD_TAPETE,
            store_id=_STORE_ID,
            category_id=_CAT_TEXTILES,
            name="Tapete de Palma",
            description="Tapete tejido a mano con fibra de palma natural",
            base_price=Decimal("120.00"),
            is_active=True,
        ),
        Product(
            id=_PROD_VASIJA,
            store_id=_STORE_ID,
            category_id=_CAT_TEXTILES,
            name="Vasija de Barro",
            description="Vasija artesanal de barro negro",
            base_price=Decimal("95.00"),
            is_active=False,  # intentionally inactive
        ),
        Product(
            id=_PROD_BOLSA,
            store_id=_STORE_ID,
            category_id=None,
            name="Bolsa de Cuero",
            description=None,  # no description on purpose
            base_price=Decimal("450.00"),
            is_active=True,
        ),
    ]
    for p in products:
        db.add(p)

    await db.commit()


@pytest.fixture(scope="function")
async def client():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_db():
        async with TestingSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    async with TestingSessionLocal() as db:
        await _seed(db)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=True,
    ) as c:
        yield c

    app.dependency_overrides.clear()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ===========================================================================
# GET /api/v1/products/search
# ===========================================================================


class TestProductSearch:
    # ------------------------------------------------------------------
    # Status codes and response shape
    # ------------------------------------------------------------------

    async def test_search_returns_200(self, client: AsyncClient):
        response = await client.get("/api/v1/products/search?q=huipil")
        assert response.status_code == 200

    async def test_search_response_has_pagination_shape(self, client: AsyncClient):
        response = await client.get("/api/v1/products/search?q=artesanal")
        data = response.json()
        assert "items" in data
        assert "page" in data
        assert "limit" in data
        assert "total" in data

    # ------------------------------------------------------------------
    # Query matching — name
    # ------------------------------------------------------------------

    async def test_search_matches_by_name(self, client: AsyncClient):
        response = await client.get("/api/v1/products/search?q=Huipil")
        data = response.json()
        assert data["total"] >= 1
        names = [item["name"] for item in data["items"]]
        assert "Huipil Bordado" in names

    async def test_search_is_case_insensitive(self, client: AsyncClient):
        response = await client.get("/api/v1/products/search?q=huipil")
        data = response.json()
        assert data["total"] >= 1

    # ------------------------------------------------------------------
    # Query matching — description
    # ------------------------------------------------------------------

    async def test_search_matches_by_description(self, client: AsyncClient):
        # "guatemalteco" only appears in the description of "Collar de Jade"
        response = await client.get("/api/v1/products/search?q=guatemalteco")
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["name"] == "Collar de Jade"

    async def test_search_matches_partial_word_in_description(
        self, client: AsyncClient
    ):
        # "artesanal" appears in descriptions of both Collar de Jade and Vasija
        # (but Vasija is inactive, so only 1 active result)
        response = await client.get("/api/v1/products/search?q=artesanal")
        data = response.json()
        active_names = [item["name"] for item in data["items"]]
        assert "Collar de Jade" in active_names

    # ------------------------------------------------------------------
    # is_active filter
    # ------------------------------------------------------------------

    async def test_search_excludes_inactive_products_by_default(
        self, client: AsyncClient
    ):
        # "Vasija de Barro" is inactive; "Barro" appears in its description
        response = await client.get("/api/v1/products/search?q=Barro")
        data = response.json()
        names = [item["name"] for item in data["items"]]
        assert "Vasija de Barro" not in names

    async def test_search_inactive_product_not_in_results(self, client: AsyncClient):
        # Broad search — inactive Vasija should never surface
        response = await client.get("/api/v1/products/search?q=artesanal")
        data = response.json()
        names = [item["name"] for item in data["items"]]
        assert "Vasija de Barro" not in names

    # ------------------------------------------------------------------
    # Empty / no-match behaviour
    # ------------------------------------------------------------------

    async def test_search_empty_query_returns_empty(self, client: AsyncClient):
        response = await client.get("/api/v1/products/search?q=")
        data = response.json()
        assert response.status_code == 200
        assert data["items"] == []
        assert data["total"] == 0

    async def test_search_no_match_returns_empty_items(self, client: AsyncClient):
        response = await client.get("/api/v1/products/search?q=xyzzy_no_match")
        data = response.json()
        assert response.status_code == 200
        assert data["items"] == []
        assert data["total"] == 0

    async def test_search_missing_q_returns_empty(self, client: AsyncClient):
        # q defaults to "" so should behave like empty query
        response = await client.get("/api/v1/products/search")
        data = response.json()
        assert response.status_code == 200
        assert data["items"] == []

    # ------------------------------------------------------------------
    # Pagination
    # ------------------------------------------------------------------

    async def test_search_default_page(self, client: AsyncClient):
        response = await client.get("/api/v1/products/search?q=de")
        data = response.json()
        assert data["page"] == 1
        assert data["limit"] == 10

    async def test_search_custom_pagination(self, client: AsyncClient):
        response = await client.get("/api/v1/products/search?q=de&page=1&limit=2")
        data = response.json()
        assert response.status_code == 200
        assert data["limit"] == 2
        assert len(data["items"]) <= 2

    async def test_search_page_beyond_results_returns_empty_items(
        self, client: AsyncClient
    ):
        response = await client.get(
            "/api/v1/products/search?q=Huipil&page=999&limit=10"
        )
        data = response.json()
        assert response.status_code == 200
        assert data["items"] == []
        assert data["total"] >= 1  # total still reflects actual count

    async def test_search_invalid_limit_returns_422(self, client: AsyncClient):
        response = await client.get("/api/v1/products/search?q=collar&limit=999")
        assert response.status_code == 422

    async def test_search_invalid_page_returns_422(self, client: AsyncClient):
        response = await client.get("/api/v1/products/search?q=collar&page=0")
        assert response.status_code == 422

    # ------------------------------------------------------------------
    # Response item shape
    # ------------------------------------------------------------------

    async def test_search_item_has_required_fields(self, client: AsyncClient):
        response = await client.get("/api/v1/products/search?q=Huipil")
        item = response.json()["items"][0]
        for field in ("id", "name", "base_price", "is_active", "created_at"):
            assert field in item, f"Missing field: {field}"

    async def test_search_item_is_active_true(self, client: AsyncClient):
        response = await client.get("/api/v1/products/search?q=Collar")
        item = response.json()["items"][0]
        assert item["is_active"] is True

    # ------------------------------------------------------------------
    # Multiple matches
    # ------------------------------------------------------------------

    async def test_search_returns_all_matching_active_products(
        self, client: AsyncClient
    ):
        # "de" appears in "Collar de Jade", "Tapete de Palma", "Bolsa de Cuero"
        response = await client.get("/api/v1/products/search?q=de&limit=100")
        data = response.json()
        names = {item["name"] for item in data["items"]}
        assert "Collar de Jade" in names
        assert "Tapete de Palma" in names
        assert "Bolsa de Cuero" in names
        # Inactive product must be absent
        assert "Vasija de Barro" not in names


# ===========================================================================
# GET /api/v1/products/autocomplete
# ===========================================================================


class TestProductAutocomplete:
    # ------------------------------------------------------------------
    # Status codes and response shape
    # ------------------------------------------------------------------

    async def test_autocomplete_returns_200(self, client: AsyncClient):
        response = await client.get("/api/v1/products/autocomplete?q=Collar")
        assert response.status_code == 200

    async def test_autocomplete_returns_a_list(self, client: AsyncClient):
        response = await client.get("/api/v1/products/autocomplete?q=Collar")
        assert isinstance(response.json(), list)

    # ------------------------------------------------------------------
    # Matching
    # ------------------------------------------------------------------

    async def test_autocomplete_matches_name(self, client: AsyncClient):
        response = await client.get("/api/v1/products/autocomplete?q=Huipil")
        data = response.json()
        assert len(data) >= 1
        assert data[0]["name"] == "Huipil Bordado"

    async def test_autocomplete_is_case_insensitive(self, client: AsyncClient):
        response = await client.get("/api/v1/products/autocomplete?q=huipil")
        data = response.json()
        assert len(data) >= 1

    async def test_autocomplete_matches_by_description(self, client: AsyncClient):
        # "guatemalteco" is only in Collar de Jade's description
        response = await client.get("/api/v1/products/autocomplete?q=guatemalteco")
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Collar de Jade"

    # ------------------------------------------------------------------
    # is_active filter
    # ------------------------------------------------------------------

    async def test_autocomplete_excludes_inactive_products(self, client: AsyncClient):
        response = await client.get("/api/v1/products/autocomplete?q=Vasija")
        data = response.json()
        names = [item["name"] for item in data]
        assert "Vasija de Barro" not in names

    # ------------------------------------------------------------------
    # Empty / no-match behaviour
    # ------------------------------------------------------------------

    async def test_autocomplete_empty_query_returns_empty_list(
        self, client: AsyncClient
    ):
        response = await client.get("/api/v1/products/autocomplete?q=")
        assert response.status_code == 200
        assert response.json() == []

    async def test_autocomplete_no_match_returns_empty_list(self, client: AsyncClient):
        response = await client.get("/api/v1/products/autocomplete?q=xyzzy_no_match")
        assert response.status_code == 200
        assert response.json() == []

    async def test_autocomplete_missing_q_returns_empty_list(self, client: AsyncClient):
        response = await client.get("/api/v1/products/autocomplete")
        assert response.status_code == 200
        assert response.json() == []

    # ------------------------------------------------------------------
    # Hard cap of 10
    # ------------------------------------------------------------------

    async def test_autocomplete_hard_cap_is_ten(self, client: AsyncClient):
        # "de" matches at least 3 active products; result must never exceed 10
        response = await client.get("/api/v1/products/autocomplete?q=de")
        data = response.json()
        assert len(data) <= 10

    # ------------------------------------------------------------------
    # Response item shape — minimal projection
    # ------------------------------------------------------------------

    async def test_autocomplete_item_has_required_fields(self, client: AsyncClient):
        response = await client.get("/api/v1/products/autocomplete?q=Collar")
        item = response.json()[0]
        for field in ("id", "name", "base_price"):
            assert field in item, f"Missing field: {field}"

    async def test_autocomplete_item_does_not_expose_variants(
        self, client: AsyncClient
    ):
        """Autocomplete must be a lean projection — no heavy relations."""
        response = await client.get("/api/v1/products/autocomplete?q=Collar")
        item = response.json()[0]
        assert "variants" not in item
        assert "store" not in item

    async def test_autocomplete_item_primary_image_url_is_none_when_no_image(
        self, client: AsyncClient
    ):
        response = await client.get("/api/v1/products/autocomplete?q=Huipil")
        item = response.json()[0]
        # No image was seeded for Huipil, so primary_image_url must be null
        assert item.get("primary_image_url") is None

    async def test_autocomplete_item_base_price_is_correct(self, client: AsyncClient):
        response = await client.get("/api/v1/products/autocomplete?q=Collar")
        item = response.json()[0]
        # Collar de Jade has base_price 280.00
        assert float(item["base_price"]) == pytest.approx(280.00)

    # ------------------------------------------------------------------
    # Does NOT collide with /{product_id} route
    # ------------------------------------------------------------------

    async def test_autocomplete_route_does_not_collide_with_product_detail(
        self, client: AsyncClient
    ):
        """Ensure FastAPI resolves /autocomplete as the literal path, not as
        a UUID product_id parameter, which would return 422 or 404."""
        response = await client.get("/api/v1/products/autocomplete?q=collar")
        # Must NOT be 422 (UUID parse error) or 404 (product not found)
        assert response.status_code == 200

    async def test_search_route_does_not_collide_with_product_detail(
        self, client: AsyncClient
    ):
        response = await client.get("/api/v1/products/search?q=collar")
        assert response.status_code == 200
