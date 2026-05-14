from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_get_products_returns_200():
    response = client.get("/api/products")

    assert response.status_code == 200


def test_get_products_has_pagination_fields():
    response = client.get("/api/products")

    data = response.json()

    assert "items" in data
    assert "page" in data
    assert "limit" in data
    assert "total" in data


def test_get_products_default_page():
    response = client.get("/api/products")

    data = response.json()

    assert data["page"] == 1
    assert data["limit"] == 10


def test_get_products_custom_pagination():
    response = client.get("/api/products?page=2&limit=5")

    data = response.json()

    assert response.status_code == 200
    assert data["page"] == 2
    assert data["limit"] == 5


def test_get_products_invalid_limit():
    response = client.get("/api/products?limit=1000")

    assert response.status_code == 422


def test_get_products_invalid_page():
    response = client.get("/api/products?page=0")

    assert response.status_code == 422


def test_get_products_category_filter():
    response = client.get("/api/products?category=home")

    assert response.status_code == 200