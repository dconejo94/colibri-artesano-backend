import uuid

from tests.factories.product_factory import (
    TEST_USER_ID,
    TEST_PRODUCT_ID,
)


async def test_remove_product_from_cart(client):
    add_resp = await client.post(
        f"/api/v1/cart/addProduct?buyer_id={TEST_USER_ID}",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "quantity": 1,
        },
    )

    store_order_id = add_resp.json()["stores"][0]["id"]

    resp = await client.delete(
        f"/api/v1/cart/removeProduct/{TEST_PRODUCT_ID}"
        f"?buyer_id={TEST_USER_ID}"
        f"&store_order_id={store_order_id}"
    )

    assert resp.status_code == 200

    data = resp.json()

    assert data["buyer_id"] == str(TEST_USER_ID)

    if data["stores"]:
        assert len(data["stores"][0]["items"]) == 0


async def test_remove_nonexistent_product_returns_404(client):
    fake_product = uuid.uuid4()

    resp = await client.delete(
        f"/api/v1/cart/removeProduct/{fake_product}"
        f"?buyer_id={TEST_USER_ID}"
        f"&store_order_id={uuid.uuid4()}"
    )

    assert resp.status_code == 404


async def test_remove_product_from_nonexistent_cart_returns_404(client):
    resp = await client.delete(
        f"/api/v1/cart/removeProduct/{TEST_PRODUCT_ID}"
        f"?buyer_id={TEST_USER_ID}"
        f"&store_order_id={uuid.uuid4()}"
    )

    assert resp.status_code == 404


async def test_remove_product_not_in_cart_returns_404(client):
    add_resp = await client.post(
        f"/api/v1/cart/addProduct?buyer_id={TEST_USER_ID}",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "quantity": 1,
        },
    )

    store_order_id = add_resp.json()["stores"][0]["id"]

    await client.delete(
        f"/api/v1/cart/removeProduct/{TEST_PRODUCT_ID}"
        f"?buyer_id={TEST_USER_ID}"
        f"&store_order_id={store_order_id}"
    )

    resp = await client.delete(
        f"/api/v1/cart/removeProduct/{TEST_PRODUCT_ID}"
        f"?buyer_id={TEST_USER_ID}"
        f"&store_order_id={store_order_id}"
    )

    assert resp.status_code == 404
