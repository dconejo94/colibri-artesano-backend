import uuid

from tests.factories.product_factory import TEST_PRODUCT_ID


async def test_add_product_success(client):
    resp = await client.post(
        "/api/v1/cart/addProduct",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "quantity": 1,
        },
    )

    assert resp.status_code == 201

    data = resp.json()

    assert len(data["stores"]) == 1
    assert len(data["stores"][0]["items"]) == 1


async def test_add_nonexistent_product_returns_404(client):
    resp = await client.post(
        "/api/v1/cart/addProduct",
        json={
            "product_id": str(uuid.uuid4()),
            "quantity": 1,
        },
    )

    assert resp.status_code == 404


async def test_add_same_product_twice_accumulates_quantity(client):
    await client.post(
        "/api/v1/cart/addProduct",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "quantity": 2,
        },
    )

    resp = await client.post(
        "/api/v1/cart/addProduct",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "quantity": 3,
        },
    )

    assert resp.status_code == 201

    data = resp.json()

    item = data["stores"][0]["items"][0]

    assert item["quantity"] == 5
