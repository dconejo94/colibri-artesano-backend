import uuid
from decimal import Decimal

from tests.factories.product_factory import (
    TEST_PRODUCT_ID,
    TEST_PRODUCT_2_ID,
    TEST_VARIANT_1_ID,
    TEST_VARIANT_2_ID,
)

from app.main import app
from app.core.security import get_current_user
from app.domain.models.user import User


async def _add(client, product_id, quantity, variant_id=None):
    body = {"product_id": str(product_id), "quantity": quantity}
    if variant_id is not None:
        body["variant_id"] = str(variant_id)
    return await client.post("/api/v1/cart/item", json=body)


async def test_update_cart_item_quantity_success(client):
    add_resp = await _add(client, TEST_PRODUCT_2_ID, 2)
    store_order_id = add_resp.json()["stores"][0]["id"]

    resp = await client.patch(
        f"/api/v1/cart/item/{TEST_PRODUCT_2_ID}"
        f"?store_order_id={store_order_id}&quantity=5"
    )

    assert resp.status_code == 200

    data = resp.json()
    item = data["stores"][0]["items"][0]

    assert item["quantity"] == 5

    expected = Decimal(item["unit_price"]) * Decimal(5)
    assert Decimal(data["total_amount"]) == expected


async def test_update_cart_item_nonexistent_product_returns_404(client):
    add_resp = await _add(client, TEST_PRODUCT_2_ID, 1)
    store_order_id = add_resp.json()["stores"][0]["id"]

    resp = await client.patch(
        f"/api/v1/cart/item/{uuid.uuid4()}?store_order_id={store_order_id}&quantity=5"
    )

    assert resp.status_code == 404


async def test_update_cart_item_not_in_cart_returns_404(client):
    # Cart holds TEST_PRODUCT; updating TEST_PRODUCT_2 (not in cart) is a 404.
    add_resp = await _add(client, TEST_PRODUCT_ID, 1, variant_id=TEST_VARIANT_1_ID)
    store_order_id = add_resp.json()["stores"][0]["id"]

    resp = await client.patch(
        f"/api/v1/cart/item/{TEST_PRODUCT_2_ID}"
        f"?store_order_id={store_order_id}&quantity=5"
    )

    assert resp.status_code == 404


async def test_update_cart_item_invalid_store_order_returns_404(client):
    await _add(client, TEST_PRODUCT_2_ID, 1)

    resp = await client.patch(
        f"/api/v1/cart/item/{TEST_PRODUCT_2_ID}"
        f"?store_order_id={uuid.uuid4()}&quantity=5"
    )

    assert resp.status_code == 404


async def test_update_cart_item_updates_totals(client):
    add_resp = await _add(client, TEST_PRODUCT_2_ID, 1)
    store_order_id = add_resp.json()["stores"][0]["id"]

    resp = await client.patch(
        f"/api/v1/cart/item/{TEST_PRODUCT_2_ID}"
        f"?store_order_id={store_order_id}&quantity=3"
    )

    assert resp.status_code == 200

    data = resp.json()
    item = data["stores"][0]["items"][0]

    assert item["quantity"] == 3

    expected_total = Decimal(item["unit_price"]) * Decimal(item["quantity"])
    assert Decimal(data["total_amount"]) == expected_total


async def test_update_cart_item_quantity_zero_returns_422(client):
    add_resp = await _add(client, TEST_PRODUCT_2_ID, 2)
    store_order_id = add_resp.json()["stores"][0]["id"]

    resp = await client.patch(
        f"/api/v1/cart/item/{TEST_PRODUCT_2_ID}"
        f"?store_order_id={store_order_id}&quantity=0"
    )

    assert resp.status_code == 422


async def test_update_cart_item_quantity_negative_returns_422(client):
    add_resp = await _add(client, TEST_PRODUCT_2_ID, 2)
    store_order_id = add_resp.json()["stores"][0]["id"]

    resp = await client.patch(
        f"/api/v1/cart/item/{TEST_PRODUCT_2_ID}"
        f"?store_order_id={store_order_id}&quantity=-1"
    )

    assert resp.status_code == 422


async def test_update_cart_item_from_other_user_cart_returns_404(client):
    add_resp = await _add(client, TEST_PRODUCT_2_ID, 2)
    store_order_id = add_resp.json()["stores"][0]["id"]

    other_user = User(
        id=uuid.UUID("00000000-0000-0000-0000-000000000088"),
        email="other@test.com",
        password_hash="hash",
        is_active=True,
        role="buyer",
    )

    async def override_other_user():
        return other_user

    app.dependency_overrides[get_current_user] = override_other_user

    try:
        resp = await client.patch(
            f"/api/v1/cart/item/{TEST_PRODUCT_2_ID}"
            f"?store_order_id={store_order_id}&quantity=5"
        )
    finally:
        del app.dependency_overrides[get_current_user]

    assert resp.status_code == 404


async def test_update_targets_the_named_variant(client):
    # Two variants of the same product are separate lines; updating one must not
    # touch the other.
    add_resp = await _add(client, TEST_PRODUCT_ID, 2, variant_id=TEST_VARIANT_1_ID)
    await _add(client, TEST_PRODUCT_ID, 1, variant_id=TEST_VARIANT_2_ID)

    store_order_id = add_resp.json()["stores"][0]["id"]

    resp = await client.patch(
        f"/api/v1/cart/item/{TEST_PRODUCT_ID}"
        f"?store_order_id={store_order_id}"
        f"&variant_id={TEST_VARIANT_1_ID}"
        f"&quantity=5"
    )

    assert resp.status_code == 200

    items = {i["variant_id"]: i for i in resp.json()["stores"][0]["items"]}

    assert items[str(TEST_VARIANT_1_ID)]["quantity"] == 5
    assert items[str(TEST_VARIANT_2_ID)]["quantity"] == 1


async def test_update_exceeding_stock_returns_409(client):
    # TEST_VARIANT_1 has stock 50.
    add_resp = await _add(client, TEST_PRODUCT_ID, 2, variant_id=TEST_VARIANT_1_ID)
    store_order_id = add_resp.json()["stores"][0]["id"]

    resp = await client.patch(
        f"/api/v1/cart/item/{TEST_PRODUCT_ID}"
        f"?store_order_id={store_order_id}"
        f"&variant_id={TEST_VARIANT_1_ID}"
        f"&quantity=51"
    )

    assert resp.status_code == 409


async def test_update_multivariant_without_variant_returns_409(client):
    add_resp = await _add(client, TEST_PRODUCT_ID, 2, variant_id=TEST_VARIANT_1_ID)
    store_order_id = add_resp.json()["stores"][0]["id"]

    resp = await client.patch(
        f"/api/v1/cart/item/{TEST_PRODUCT_ID}"
        f"?store_order_id={store_order_id}&quantity=5"
    )

    assert resp.status_code == 409
