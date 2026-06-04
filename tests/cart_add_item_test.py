import uuid

from tests.factories.product_factory import (
    TEST_USER_ID,
    TEST_PRODUCT_ID,
)


async def test_add_same_product_twice_increases_quantity(client):
    await client.post(
        f"/api/v1/cart/addProduct?buyer_id={TEST_USER_ID}",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "quantity": 1,
        },
    )

    resp = await client.post(
        f"/api/v1/cart/addProduct?buyer_id={TEST_USER_ID}",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "quantity": 3,
        },
    )

    data = resp.json()

    item = data["stores"][0]["items"][0]

    assert item["quantity"] == 4


async def test_add_product_nonexistent_user_returns_404(client):
    fake_user = uuid.uuid4()

    resp = await client.post(
        f"/api/v1/cart/addProduct?buyer_id={fake_user}",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "quantity": 1,
        },
    )

    assert resp.status_code == 404


async def test_add_nonexistent_product_returns_404(client):
    fake_product = uuid.uuid4()

    resp = await client.post(
        f"/api/v1/cart/addProduct?buyer_id={TEST_USER_ID}",
        json={
            "product_id": str(fake_product),
            "quantity": 1,
        },
    )

    assert resp.status_code == 404


async def test_add_product_quantity_zero_returns_422(client):
    resp = await client.post(
        f"/api/v1/cart/addProduct?buyer_id={TEST_USER_ID}",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "quantity": 0,
        },
    )

    assert resp.status_code == 422
