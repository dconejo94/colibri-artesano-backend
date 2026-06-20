"""Tests for Product write operations and cascade delete behavior."""

import uuid

from tests.factories.product_factory import (
    TEST_STORE_ID,
    TEST_CATEGORY_ID,
    TEST_PRODUCT_ID,
)


# ── Create Product ────────────────────────────────────────────────


async def test_create_product_success(client):
    body = {
        "category_id": str(TEST_CATEGORY_ID),
        "name": "New Product",
        "description": "A test product",
        "base_price": 100.00,
    }

    resp = await client.post(
        f"/api/v1/stores/{TEST_STORE_ID}/products",
        json=body,
    )

    assert resp.status_code == 201

    data = resp.json()

    assert data["name"] == "New Product"
    assert data["store_id"] == str(TEST_STORE_ID)
    assert data["stock"] == 0


async def test_create_product_creates_default_variant(client):
    # Every product must be sellable, so creation seeds one default variant.
    body = {
        "category_id": str(TEST_CATEGORY_ID),
        "name": "Variant-less Product",
        "base_price": 12.00,
    }

    resp = await client.post(
        f"/api/v1/stores/{TEST_STORE_ID}/products",
        json=body,
    )
    assert resp.status_code == 201
    product_id = resp.json()["id"]

    variants = await client.get(f"/api/v1/products/{product_id}/variants")
    assert variants.status_code == 200
    assert len(variants.json()) == 1


async def test_create_product_bad_category_returns_404(client):
    """Non-existent category_id should 404, not 500."""
    fake_cat = uuid.uuid4()
    body = {
        "category_id": str(fake_cat),
        "name": "Orphan",
        "base_price": 50.00,
    }
    resp = await client.post(f"/api/v1/stores/{TEST_STORE_ID}/products", json=body)

    assert resp.status_code == 404


async def test_create_product_missing_required_fields(client):
    resp = await client.post(
        f"/api/v1/stores/{TEST_STORE_ID}/products",
        json={"name": "No price"},
    )

    assert resp.status_code == 422


# ── Update Product ────────────────────────────────────────────────


async def test_update_product_success(client):
    resp = await client.put(
        f"/api/v1/products/{TEST_PRODUCT_ID}",
        json={"name": "Updated Product Name"},
    )

    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated Product Name"


async def test_update_product_bad_category(client):
    fake_cat = uuid.uuid4()
    resp = await client.put(
        f"/api/v1/products/{TEST_PRODUCT_ID}",
        json={"category_id": str(fake_cat)},
    )

    assert resp.status_code == 404


async def test_update_product_not_found(client):
    fake_id = uuid.uuid4()
    resp = await client.put(f"/api/v1/products/{fake_id}", json={"name": "Ghost"})

    assert resp.status_code == 404


# ── Delete Product (cascade) ─────────────────────────────────────


async def test_delete_product_with_children(client):
    """Delete a product that has images/variants attached → 204 (cascade)."""
    # 1. Create a fresh product
    body = {
        "category_id": str(TEST_CATEGORY_ID),
        "name": "Cascade Test",
        "base_price": 10.00,
    }
    product_resp = await client.post(
        f"/api/v1/stores/{TEST_STORE_ID}/products", json=body
    )
    pid = product_resp.json()["id"]

    # 2. Add an image
    img_resp = await client.post(
        f"/api/v1/products/{pid}/images",
        json={"image_url": "https://example.com/img.jpg", "is_primary": True},
    )
    assert img_resp.status_code == 201

    # 3. Add a variant
    var_resp = await client.post(
        f"/api/v1/products/{pid}/variants",
        json={"name": "Color", "value": "Rojo", "stock_quantity": 5},
    )
    assert var_resp.status_code == 201

    # 4. Delete the product — should cascade
    del_resp = await client.delete(f"/api/v1/products/{pid}")
    assert del_resp.status_code == 204

    # 5. Confirm gone
    get_resp = await client.get(f"/api/v1/products/{pid}")
    assert get_resp.status_code == 404


async def test_delete_product_not_found(client):
    fake_id = uuid.uuid4()
    resp = await client.delete(f"/api/v1/products/{fake_id}")

    assert resp.status_code == 404
