"""Tests for Orders: creation, server-side pricing, validation, and edge cases."""

import uuid
from decimal import Decimal

from tests.factories.product_factory import (
    TEST_USER_ID,
    TEST_STORE_ID,
    TEST_CATEGORY_ID,
    TEST_PRODUCT_ID,
)


# ── Helpers ───────────────────────────────────────────────────────


async def _create_variant(client, product_id, name, value, modifier):
    resp = await client.post(
        f"/api/v1/products/{product_id}/variants",
        json={
            "name": name,
            "value": value,
            "price_modifier": float(modifier),
            "stock_quantity": 50,
        },
    )
    assert resp.status_code == 201
    return resp.json()["id"]


# ── Happy Path ────────────────────────────────────────────────────


async def test_create_order_success(client):
    """Basic order with one item, no variant."""
    body = {
        "buyer_id": str(TEST_USER_ID),
        "items": [
            {"product_id": str(TEST_PRODUCT_ID), "quantity": 2},
        ],
    }
    resp = await client.post("/api/v1/orders/", json=body)

    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "pending"
    assert Decimal(data["total_amount"]) == Decimal("20.00")
    assert len(data["store_orders"]) == 1
    assert len(data["store_orders"][0]["items"]) == 1
    assert Decimal(data["store_orders"][0]["items"][0]["unit_price"]) == Decimal(
        "10.00"
    )


async def test_create_order_with_variant_applies_modifier(client):
    """Price = base_price + variant.price_modifier, computed server-side."""
    variant_id = await _create_variant(
        client, TEST_PRODUCT_ID, "Size", "XL", Decimal("5.00")
    )

    body = {
        "buyer_id": str(TEST_USER_ID),
        "items": [
            {
                "product_id": str(TEST_PRODUCT_ID),
                "variant_id": variant_id,
                "quantity": 1,
            },
        ],
    }
    resp = await client.post("/api/v1/orders/", json=body)

    assert resp.status_code == 201
    data = resp.json()
    # base_price=10 + modifier=5 → 15
    assert Decimal(data["total_amount"]) == Decimal("15.00")
    assert Decimal(data["store_orders"][0]["items"][0]["unit_price"]) == Decimal(
        "15.00"
    )


async def test_get_order_success(client):
    create_resp = await client.post(
        "/api/v1/orders/",
        json={
            "buyer_id": str(TEST_USER_ID),
            "items": [{"product_id": str(TEST_PRODUCT_ID), "quantity": 1}],
        },
    )
    order_id = create_resp.json()["id"]

    resp = await client.get(f"/api/v1/orders/{order_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == order_id


async def test_get_order_not_found(client):
    fake_id = uuid.uuid4()
    resp = await client.get(f"/api/v1/orders/{fake_id}")

    assert resp.status_code == 404


async def test_list_buyer_orders(client):
    await client.post(
        "/api/v1/orders/",
        json={
            "buyer_id": str(TEST_USER_ID),
            "items": [{"product_id": str(TEST_PRODUCT_ID), "quantity": 1}],
        },
    )

    resp = await client.get(f"/api/v1/orders/?buyer_id={TEST_USER_ID}")

    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1


# ── DTO Validation ────────────────────────────────────────────────


async def test_order_empty_items_rejected(client):
    """Empty items list → 422 (min_length=1)."""
    body = {"buyer_id": str(TEST_USER_ID), "items": []}
    resp = await client.post("/api/v1/orders/", json=body)

    assert resp.status_code == 422


async def test_order_quantity_zero_rejected(client):
    """quantity=0 → 422 (gt=0)."""
    body = {
        "buyer_id": str(TEST_USER_ID),
        "items": [{"product_id": str(TEST_PRODUCT_ID), "quantity": 0}],
    }
    resp = await client.post("/api/v1/orders/", json=body)

    assert resp.status_code == 422


async def test_order_quantity_negative_rejected(client):
    """quantity=-5 → 422 (gt=0)."""
    body = {
        "buyer_id": str(TEST_USER_ID),
        "items": [{"product_id": str(TEST_PRODUCT_ID), "quantity": -5}],
    }
    resp = await client.post("/api/v1/orders/", json=body)

    assert resp.status_code == 422


# ── Existence & Ownership Checks ─────────────────────────────────


async def test_order_nonexistent_buyer_returns_404(client):
    """Non-existent buyer_id → 404, not 500."""
    fake_buyer = uuid.uuid4()
    body = {
        "buyer_id": str(fake_buyer),
        "items": [{"product_id": str(TEST_PRODUCT_ID), "quantity": 1}],
    }
    resp = await client.post("/api/v1/orders/", json=body)

    assert resp.status_code == 404


async def test_order_nonexistent_product_returns_404(client):
    fake_product = uuid.uuid4()
    body = {
        "buyer_id": str(TEST_USER_ID),
        "items": [{"product_id": str(fake_product), "quantity": 1}],
    }
    resp = await client.post("/api/v1/orders/", json=body)

    assert resp.status_code == 404


async def test_order_variant_wrong_product_returns_404(client):
    """Variant belonging to product A cannot be used when ordering product B."""
    variant_id = await _create_variant(
        client, TEST_PRODUCT_ID, "Owned", "V1", Decimal("0")
    )

    # Create a second product
    prod_resp = await client.post(
        f"/api/v1/stores/{TEST_STORE_ID}/products",
        json={
            "category_id": str(TEST_CATEGORY_ID),
            "name": "Other Product",
            "base_price": 99.00,
        },
    )
    other_product_id = prod_resp.json()["id"]

    body = {
        "buyer_id": str(TEST_USER_ID),
        "items": [
            {
                "product_id": other_product_id,
                "variant_id": variant_id,
                "quantity": 1,
            }
        ],
    }
    resp = await client.post("/api/v1/orders/", json=body)

    assert resp.status_code == 404


async def test_order_nonexistent_variant_returns_404(client):
    fake_variant = uuid.uuid4()
    body = {
        "buyer_id": str(TEST_USER_ID),
        "items": [
            {
                "product_id": str(TEST_PRODUCT_ID),
                "variant_id": str(fake_variant),
                "quantity": 1,
            }
        ],
    }
    resp = await client.post("/api/v1/orders/", json=body)

    assert resp.status_code == 404
