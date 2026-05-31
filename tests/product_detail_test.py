from tests.factories.product_factory import TEST_PRODUCT_ID
import uuid


async def test_get_product_by_id_success(client):
    response = await client.get(f"/api/v1/products/{TEST_PRODUCT_ID}")

    # Assert status
    assert response.status_code == 200

    data = response.json()

    # Assert structure
    assert "id" in data
    assert "name" in data
    assert "base_price" in data
    assert "is_active" in data


async def test_get_product_by_id_not_found(client):
    fake_id = uuid.uuid4()
    response = await client.get(f"/api/v1/products/{fake_id}")

    assert response.status_code == 404

    data = response.json()
    assert data["detail"] == "Product not found"


async def test_get_product_by_id_response_schema(client):
    response = await client.get(f"/api/v1/products/{TEST_PRODUCT_ID}")

    assert response.status_code == 200

    data = response.json()

    expected_fields = {
        "id",
        "store_id",
        "category_id",
        "name",
        "description",
        "base_price",
        "is_active",
        "created_at",
        "images",
        "variants",
    }

    assert expected_fields.issubset(set(data.keys()))
