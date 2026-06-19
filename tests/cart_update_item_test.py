import uuid
from decimal import Decimal

from tests.factories.product_factory import TEST_PRODUCT_ID, TEST_PRODUCT_2_ID


async def test_update_cart_item_quantity_success(client):
    add_resp = await client.post(
        "/api/v1/cart/item",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "quantity": 2,
        },
    )

    store_order_id = add_resp.json()["stores"][0]["id"]

    resp = await client.patch(
        f"/api/v1/cart/item/{TEST_PRODUCT_ID}"
        f"?store_order_id={store_order_id}&quantity=5"
    )

    assert resp.status_code == 200

    data = resp.json()

    item = data["stores"][0]["items"][0]

    assert item["quantity"] == 5


async def test_update_cart_item_nonexistent_product_returns_404(client):
    add_resp = await client.post(
        "/api/v1/cart/item",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "quantity": 1,
        },
    )

    store_order_id = add_resp.json()["stores"][0]["id"]

    resp = await client.patch(
        f"/api/v1/cart/item/{uuid.uuid4()}"
        f"?store_order_id={store_order_id}&quantity=5"
    )

    assert resp.status_code == 404


async def test_update_cart_item_not_in_cart_returns_404(client):
    add_resp = await client.post(
        "/api/v1/cart/item",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "quantity": 1,
        },
    )

    store_order_id = add_resp.json()["stores"][0]["id"]

    resp = await client.patch(
        f"/api/v1/cart/item/{TEST_PRODUCT_2_ID}"
        f"?store_order_id={store_order_id}&quantity=5"
    )

    assert resp.status_code == 404


async def test_update_cart_item_invalid_store_order_returns_404(client):
    await client.post(
        "/api/v1/cart/item",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "quantity": 1,
        },
    )

    resp = await client.patch(
        f"/api/v1/cart/item/{TEST_PRODUCT_ID}"
        f"?store_order_id={uuid.uuid4()}&quantity=5"
    )

    assert resp.status_code == 404


async def test_update_cart_item_updates_totals(client):
    add_resp = await client.post(
        "/api/v1/cart/item",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "quantity": 1,
        },
    )

    store_order_id = add_resp.json()["stores"][0]["id"]

    resp = await client.patch(
        f"/api/v1/cart/item/{TEST_PRODUCT_ID}"
        f"?store_order_id={store_order_id}&quantity=3"
    )

    assert resp.status_code == 200

    data = resp.json()

    item = data["stores"][0]["items"][0]

    assert item["quantity"] == 3

    expected_total = Decimal(item["unit_price"]) * Decimal(item["quantity"])

    assert Decimal(data["total_amount"]) == expected_total
