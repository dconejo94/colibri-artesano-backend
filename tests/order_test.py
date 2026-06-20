"""Tests for checkout: the cart (MainOrder status="cart") is converted into a
placed order (status="placed"). Checkout consumes the buyer's cart and no longer
accepts an items body — item validation/pricing happen when adding to the cart.
"""

import uuid
from decimal import Decimal

from tests.conftest import TestingSessionLocal
from app.domain.models.product_variant import ProductVariant

from tests.factories.product_factory import (
    TEST_PRODUCT_ID,
    TEST_VARIANT_1_ID,
    TEST_VARIANT_2_ID,
)


async def _add_to_cart(client, product_id, quantity, variant_id=TEST_VARIANT_1_ID):
    body = {"product_id": str(product_id), "quantity": quantity}
    if variant_id is not None:
        body["variant_id"] = str(variant_id)
    resp = await client.post("/api/v1/cart/item", json=body)
    assert resp.status_code == 201
    return resp


# ── Checkout converts the cart ────────────────────────────────────


async def test_checkout_converts_cart(client):
    await _add_to_cart(client, TEST_PRODUCT_ID, 2)

    resp = await client.post("/api/v1/orders/")

    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "placed"
    assert Decimal(data["total_amount"]) == Decimal("20.00")
    assert len(data["store_orders"]) == 1
    assert len(data["store_orders"][0]["items"]) == 1


async def test_checkout_with_variant_uses_variant_price(client):
    # base 10.00 + variant 2 modifier 15.00 = 25.00
    await _add_to_cart(client, TEST_PRODUCT_ID, 1, variant_id=TEST_VARIANT_2_ID)

    resp = await client.post("/api/v1/orders/")

    assert resp.status_code == 201
    assert Decimal(resp.json()["total_amount"]) == Decimal("25.00")


async def test_checkout_empty_cart_returns_409(client):
    resp = await client.post("/api/v1/orders/")

    assert resp.status_code == 409


async def test_checkout_insufficient_stock_returns_409(client):
    # Add within stock, then the variant's stock drops below the cart quantity
    # before checkout — the checkout guard must catch it.
    await _add_to_cart(client, TEST_PRODUCT_ID, 5, variant_id=TEST_VARIANT_1_ID)

    async with TestingSessionLocal() as db:
        variant = await db.get(ProductVariant, TEST_VARIANT_1_ID)
        variant.stock_quantity = 1
        await db.commit()

    resp = await client.post("/api/v1/orders/")

    assert resp.status_code == 409
    assert "stock" in resp.json()["detail"].lower()


# ── Cart vs order separation ──────────────────────────────────────


async def test_cart_emptied_after_checkout(client):
    await _add_to_cart(client, TEST_PRODUCT_ID, 1)
    await client.post("/api/v1/orders/")

    resp = await client.get("/api/v1/cart/")

    assert resp.status_code == 200
    assert resp.json()["stores"] == []


async def test_cart_not_in_order_history(client):
    # A cart that has not been checked out must not appear as an order.
    await _add_to_cart(client, TEST_PRODUCT_ID, 1)

    resp = await client.get("/api/v1/orders/")

    assert resp.status_code == 200
    assert resp.json()["total"] == 0


async def test_placed_order_in_history(client):
    await _add_to_cart(client, TEST_PRODUCT_ID, 1)
    await client.post("/api/v1/orders/")

    resp = await client.get("/api/v1/orders/")

    assert resp.status_code == 200
    assert resp.json()["total"] == 1


# ── Read a placed order ───────────────────────────────────────────


async def test_get_placed_order_by_id(client):
    await _add_to_cart(client, TEST_PRODUCT_ID, 1)
    order_id = (await client.post("/api/v1/orders/")).json()["id"]

    resp = await client.get(f"/api/v1/orders/{order_id}")

    assert resp.status_code == 200
    assert resp.json()["id"] == order_id


async def test_get_order_not_found(client):
    resp = await client.get(f"/api/v1/orders/{uuid.uuid4()}")

    assert resp.status_code == 404
