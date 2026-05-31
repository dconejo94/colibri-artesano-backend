from tests.factories.product_factory import TEST_CATEGORY_ID

async def test_get_products_returns_200(client):
    response = await client.get("/api/v1/products")

    assert response.status_code == 200


async def test_get_products_has_pagination_fields(client):
    response = await client.get("/api/v1/products")

    data = response.json()

    assert "items" in data
    assert "page" in data
    assert "limit" in data
    assert "total" in data


async def test_get_products_default_page(client):
    response = await client.get("/api/v1/products")

    data = response.json()

    assert data["page"] == 1
    assert data["limit"] == 10


async def test_get_products_custom_pagination(client):
    response = await client.get("/api/v1/products?page=2&limit=5")

    data = response.json()

    assert response.status_code == 200
    assert data["page"] == 2
    assert data["limit"] == 5


async def test_get_products_invalid_limit(client):
    response = await client.get("/api/v1/products?limit=1000")

    assert response.status_code == 422


async def test_get_products_invalid_page(client):
    response = await client.get("/api/v1/products?page=0")

    assert response.status_code == 422


async def test_get_products_category_filter(client):
    response = await client.get(f"/api/v1/products?category_id={TEST_CATEGORY_ID}")

    assert response.status_code == 200
