import uuid

from app.main import app
from app.core.security import get_current_user
from app.domain.models.user import User


from tests.factories.product_factory import (
    TEST_PRODUCT_ID,
    TEST_PRODUCT_2_ID,
    TEST_VARIANT_1_ID,
    TEST_VARIANT_2_ID,
)


async def test_remove_product_success(client):
    add_resp = await client.post(
        "/api/v1/cart/item",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "variant_id": str(TEST_VARIANT_1_ID),
            "quantity": 2,
        },
    )

    store_order_id = add_resp.json()["stores"][0]["id"]

    resp = await client.delete(
        f"/api/v1/cart/item/{TEST_PRODUCT_ID}"
        f"?variant_id={TEST_VARIANT_1_ID}"
        f"&store_order_id={store_order_id}"
    )

    assert resp.status_code == 200

    data = resp.json()

    # Removing the store's last item clears the empty store order from the cart.
    assert data["stores"] == []


async def test_remove_single_variant_product_without_variant(client):
    # TEST_PRODUCT_2 has one variant, so remove resolves it without variant_id.
    add_resp = await client.post(
        "/api/v1/cart/item",
        json={
            "product_id": str(TEST_PRODUCT_2_ID),
            "quantity": 2,
        },
    )

    store_order_id = add_resp.json()["stores"][0]["id"]

    resp = await client.delete(
        f"/api/v1/cart/item/{TEST_PRODUCT_2_ID}?store_order_id={store_order_id}"
    )

    assert resp.status_code == 200

    data = resp.json()

    assert data["stores"] == []


async def test_remove_variant_not_in_cart_returns_404(client):
    # Add variant 1, then try to remove variant 2 (a real variant not in cart).
    add_resp = await client.post(
        "/api/v1/cart/item",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "variant_id": str(TEST_VARIANT_1_ID),
            "quantity": 1,
        },
    )

    store_order_id = add_resp.json()["stores"][0]["id"]

    resp = await client.delete(
        f"/api/v1/cart/item/{TEST_PRODUCT_ID}"
        f"?variant_id={TEST_VARIANT_2_ID}"
        f"&store_order_id={store_order_id}"
    )

    assert resp.status_code == 404


async def test_remove_product_not_in_cart_returns_404(client):
    add_resp = await client.post(
        "/api/v1/cart/item",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "variant_id": str(TEST_VARIANT_1_ID),
            "quantity": 1,
        },
    )

    store_order_id = add_resp.json()["stores"][0]["id"]

    await client.delete(
        f"/api/v1/cart/item/{TEST_PRODUCT_ID}"
        f"?variant_id={TEST_VARIANT_1_ID}"
        f"&store_order_id={store_order_id}"
    )

    resp = await client.delete(
        f"/api/v1/cart/item/{TEST_PRODUCT_ID}"
        f"?variant_id={TEST_VARIANT_1_ID}"
        f"&store_order_id={store_order_id}"
    )

    assert resp.status_code == 404


async def test_remove_invalid_store_order_returns_404(client):
    resp = await client.delete(
        f"/api/v1/cart/item/{TEST_PRODUCT_ID}"
        f"?variant_id={TEST_VARIANT_1_ID}"
        f"&store_order_id={uuid.uuid4()}"
    )

    assert resp.status_code == 404


async def test_remove_product_from_other_user_cart_returns_404(client):
    add_resp = await client.post(
        "/api/v1/cart/item",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "variant_id": str(TEST_VARIANT_1_ID),
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
        resp = await client.delete(
            f"/api/v1/cart/item/{TEST_PRODUCT_ID}"
            f"?variant_id={TEST_VARIANT_1_ID}"
            f"&store_order_id={store_order_id}"
        )
    finally:
        del app.dependency_overrides[get_current_user]

    assert resp.status_code == 404


async def test_remove_from_placed_order_returns_404(client):
    # A checked-out order is no longer a cart; the cart must not mutate it.
    add_resp = await client.post(
        "/api/v1/cart/item",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "variant_id": str(TEST_VARIANT_1_ID),
            "quantity": 2,
        },
    )
    store_order_id = add_resp.json()["stores"][0]["id"]

    place = await client.post("/api/v1/orders/")
    assert place.status_code == 201

    resp = await client.delete(
        f"/api/v1/cart/item/{TEST_PRODUCT_ID}"
        f"?variant_id={TEST_VARIANT_1_ID}"
        f"&store_order_id={store_order_id}"
    )

    assert resp.status_code == 404


async def test_remove_only_requested_variant(client):
    add_resp = await client.post(
        "/api/v1/cart/item",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "variant_id": str(TEST_VARIANT_1_ID),
            "quantity": 1,
        },
    )

    await client.post(
        "/api/v1/cart/item",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "variant_id": str(TEST_VARIANT_2_ID),
            "quantity": 1,
        },
    )

    store_order_id = add_resp.json()["stores"][0]["id"]

    resp = await client.delete(
        f"/api/v1/cart/item/{TEST_PRODUCT_ID}"
        f"?variant_id={TEST_VARIANT_1_ID}"
        f"&store_order_id={store_order_id}"
    )

    assert resp.status_code == 200

    items = resp.json()["stores"][0]["items"]

    assert len(items) == 1
    assert items[0]["variant_id"] == str(TEST_VARIANT_2_ID)
