import uuid

from tests.factories.product_factory import TEST_PRODUCT_ID


async def test_remove_product_success(client):
    add_resp = await client.post(
        "/api/v1/cart/addProduct",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "quantity": 2,
        },
    )

    store_order_id = add_resp.json()["stores"][0]["id"]

    resp = await client.delete(
        f"/api/v1/cart/removeProduct/{TEST_PRODUCT_ID}"
        f"?store_order_id={store_order_id}"
    )

    assert resp.status_code == 200

    data = resp.json()

    assert len(data["stores"]) == 1
    assert data["stores"][0]["items"] == []

async def test_remove_nonexistent_product_returns_404(client):
    add_resp = await client.post(
        "/api/v1/cart/addProduct",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "quantity": 1,
        },
    )

    store_order_id = add_resp.json()["stores"][0]["id"]

    resp = await client.delete(
        f"/api/v1/cart/removeProduct/{uuid.uuid4()}"
        f"?store_order_id={store_order_id}"
    )

    assert resp.status_code == 404


async def test_remove_product_not_in_cart_returns_404(client):
    add_resp = await client.post(
        "/api/v1/cart/addProduct",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "quantity": 1,
        },
    )

    store_order_id = add_resp.json()["stores"][0]["id"]

    await client.delete(
        f"/api/v1/cart/removeProduct/{TEST_PRODUCT_ID}"
        f"?store_order_id={store_order_id}"
    )

    resp = await client.delete(
        f"/api/v1/cart/removeProduct/{TEST_PRODUCT_ID}"
        f"?store_order_id={store_order_id}"
    )

    assert resp.status_code == 404


async def test_remove_invalid_store_order_returns_404(client):
    resp = await client.delete(
        f"/api/v1/cart/removeProduct/{TEST_PRODUCT_ID}"
        f"?store_order_id={uuid.uuid4()}"
    )

    assert resp.status_code == 404