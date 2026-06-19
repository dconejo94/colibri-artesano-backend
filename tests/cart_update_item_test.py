import uuid
from decimal import Decimal

from tests.factories.product_factory import TEST_PRODUCT_ID, TEST_PRODUCT_2_ID

from app.main import app
from app.core.security import get_current_user
from app.domain.models.user import User


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
        f"/api/v1/cart/item/{uuid.uuid4()}?store_order_id={store_order_id}&quantity=5"
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
        f"/api/v1/cart/item/{TEST_PRODUCT_ID}?store_order_id={uuid.uuid4()}&quantity=5"
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


async def test_update_cart_item_quantity_zero_returns_400(client):
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
        f"?store_order_id={store_order_id}&quantity=0"
    )

    assert resp.status_code == 422


async def test_update_cart_item_quantity_negative_returns_400(client):
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
        f"?store_order_id={store_order_id}&quantity=-1"
    )

    assert resp.status_code == 422


async def test_update_cart_item_from_other_user_cart_returns_404(client):
    add_resp = await client.post(
        "/api/v1/cart/item",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "quantity": 2,
        },
    )

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
            f"/api/v1/cart/item/{TEST_PRODUCT_ID}"
            f"?store_order_id={store_order_id}&quantity=5"
        )
    finally:
        del app.dependency_overrides[get_current_user]

    assert resp.status_code == 404
