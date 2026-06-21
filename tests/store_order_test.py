"""Tests for Store Order management (seller-side)."""

import uuid

from tests.factories.product_factory import (
    TEST_STORE_ID,
    TEST_PRODUCT_ID,
    TEST_VARIANT_1_ID,
)


async def _create_order(client):
    await client.post(
        "/api/v1/cart/item",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "variant_id": str(TEST_VARIANT_1_ID),
            "quantity": 1,
        },
    )
    resp = await client.post("/api/v1/orders/")
    return resp.json()


async def test_list_store_orders(client):
    await _create_order(client)

    resp = await client.get(f"/api/v1/stores/{TEST_STORE_ID}/orders")

    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1


async def test_update_store_order_status(client):
    order = await _create_order(client)
    store_order_id = order["store_orders"][0]["id"]

    resp = await client.patch(
        f"/api/v1/stores/{TEST_STORE_ID}/orders/{store_order_id}/status",
        json={"seller_status": "shipped"},
    )

    assert resp.status_code == 200
    assert resp.json()["seller_status"] == "shipped"


async def test_update_store_order_not_found(client):
    fake_id = uuid.uuid4()
    resp = await client.patch(
        f"/api/v1/stores/{TEST_STORE_ID}/orders/{fake_id}/status",
        json={"seller_status": "shipped"},
    )

    assert resp.status_code == 404
