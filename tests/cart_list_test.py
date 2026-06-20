from decimal import Decimal

from tests.factories.product_factory import (
    TEST_USER_ID,
    TEST_PRODUCT_2_ID,
)


async def test_get_empty_cart(client):
    resp = await client.get("/api/v1/cart/")

    assert resp.status_code == 200

    data = resp.json()

    assert data["buyer_id"] == str(TEST_USER_ID)
    assert Decimal(data["total_amount"]) == Decimal("0.00")
    assert data["stores"] == []


async def test_get_cart_with_products(client):
    await client.post(
        "/api/v1/cart/item",
        json={
            "product_id": str(TEST_PRODUCT_2_ID),
            "quantity": 2,
        },
    )

    resp = await client.get("/api/v1/cart/")

    assert resp.status_code == 200

    data = resp.json()

    assert data["buyer_id"] == str(TEST_USER_ID)
    assert len(data["stores"]) == 1
    assert len(data["stores"][0]["items"]) == 1
    assert data["stores"][0]["items"][0]["quantity"] == 2
