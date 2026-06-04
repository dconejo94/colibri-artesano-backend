import uuid
from decimal import Decimal

from tests.factories.product_factory import (
    TEST_USER_ID,
    TEST_PRODUCT_ID,
)


async def test_get_empty_cart(client):
    resp = await client.get(f"/api/v1/cart/?buyer_id={TEST_USER_ID}")

    assert resp.status_code == 200

    data = resp.json()

    assert data["buyer_id"] == str(TEST_USER_ID)
    assert Decimal(data["total_amount"]) == Decimal("0.00")
    assert data["stores"] == []


async def test_get_cart_with_products(client):
    await client.post(
        f"/api/v1/cart/addProduct?buyer_id={TEST_USER_ID}",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "quantity": 2,
        },
    )

    resp = await client.get(f"/api/v1/cart/?buyer_id={TEST_USER_ID}")

    assert resp.status_code == 200

    data = resp.json()

    assert data["buyer_id"] == str(TEST_USER_ID)
    assert len(data["stores"]) == 1
    assert len(data["stores"][0]["items"]) == 1


async def test_get_cart_nonexistent_user_returns_404(client):
    fake_user = uuid.uuid4()

    resp = await client.get(f"/api/v1/cart/?buyer_id={fake_user}")

    assert resp.status_code == 404
