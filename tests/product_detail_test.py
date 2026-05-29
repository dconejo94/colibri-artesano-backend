async def test_get_product_by_id_success(client):
    response = await client.get("/api/v1/products/1")

    # Assert status
    assert response.status_code == 200

    data = response.json()

    # Assert structure
    assert "id" in data
    assert "name" in data
    assert "price" in data
    assert "stock" in data


async def test_get_product_by_id_not_found(client):
    response = await client.get("/api/v1/products/999999")

    assert response.status_code == 404

    data = response.json()
    assert data["detail"] == "Product not found"


async def test_get_product_by_id_response_schema(client):
    response = await client.get("/api/v1/products/1")

    assert response.status_code == 200

    data = response.json()

    expected_fields = {
        "id",
        "name",
        "description",
        "price",
        "stock",
        "image_url",
        "category",
    }

    assert expected_fields.issubset(set(data.keys()))
