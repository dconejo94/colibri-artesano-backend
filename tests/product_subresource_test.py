"""Tests for Product Image and Variant sub-resource ownership enforcement."""

import uuid

from tests.factories.product_factory import (
    TEST_PRODUCT_ID,
)


# ── Images ────────────────────────────────────────────────────────


async def test_add_image_success(client):
    resp = await client.post(
        f"/api/v1/products/{TEST_PRODUCT_ID}/images",
        json={"image_url": "https://example.com/a.jpg", "is_primary": False},
    )

    assert resp.status_code == 201
    assert resp.json()["image_url"] == "https://example.com/a.jpg"


async def test_list_images(client):
    await client.post(
        f"/api/v1/products/{TEST_PRODUCT_ID}/images",
        json={"image_url": "https://example.com/b.jpg"},
    )

    resp = await client.get(f"/api/v1/products/{TEST_PRODUCT_ID}/images")

    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_delete_image_wrong_product_returns_404(client):
    """Deleting an image through a different product_id must fail."""
    img_resp = await client.post(
        f"/api/v1/products/{TEST_PRODUCT_ID}/images",
        json={"image_url": "https://example.com/owned.jpg"},
    )
    image_id = img_resp.json()["id"]

    fake_product = uuid.uuid4()
    resp = await client.delete(f"/api/v1/products/{fake_product}/images/{image_id}")

    assert resp.status_code == 404


async def test_delete_image_correct_product(client):
    img_resp = await client.post(
        f"/api/v1/products/{TEST_PRODUCT_ID}/images",
        json={"image_url": "https://example.com/delete-me.jpg"},
    )
    image_id = img_resp.json()["id"]

    resp = await client.delete(f"/api/v1/products/{TEST_PRODUCT_ID}/images/{image_id}")

    assert resp.status_code == 204


async def test_set_primary_wrong_product_returns_404(client):
    """Setting primary through the wrong product URL must 404."""
    img_resp = await client.post(
        f"/api/v1/products/{TEST_PRODUCT_ID}/images",
        json={"image_url": "https://example.com/primary.jpg"},
    )
    image_id = img_resp.json()["id"]

    fake_product = uuid.uuid4()
    resp = await client.patch(
        f"/api/v1/products/{fake_product}/images/{image_id}/primary"
    )

    assert resp.status_code == 404


# ── Variants ──────────────────────────────────────────────────────


async def test_add_variant_success(client):
    resp = await client.post(
        f"/api/v1/products/{TEST_PRODUCT_ID}/variants",
        json={"name": "Size", "value": "Large", "stock_quantity": 10},
    )

    assert resp.status_code == 201
    assert resp.json()["name"] == "Size"


async def test_list_variants(client):
    await client.post(
        f"/api/v1/products/{TEST_PRODUCT_ID}/variants",
        json={"name": "Color", "value": "Blue"},
    )

    resp = await client.get(f"/api/v1/products/{TEST_PRODUCT_ID}/variants")

    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_update_variant_wrong_product_returns_404(client):
    var_resp = await client.post(
        f"/api/v1/products/{TEST_PRODUCT_ID}/variants",
        json={"name": "Material", "value": "Wood"},
    )
    variant_id = var_resp.json()["id"]

    fake_product = uuid.uuid4()
    resp = await client.put(
        f"/api/v1/products/{fake_product}/variants/{variant_id}",
        json={"value": "Stone"},
    )

    assert resp.status_code == 404


async def test_delete_variant_wrong_product_returns_404(client):
    var_resp = await client.post(
        f"/api/v1/products/{TEST_PRODUCT_ID}/variants",
        json={"name": "Weight", "value": "1kg"},
    )
    variant_id = var_resp.json()["id"]

    fake_product = uuid.uuid4()
    resp = await client.delete(f"/api/v1/products/{fake_product}/variants/{variant_id}")

    assert resp.status_code == 404


async def test_delete_variant_correct_product(client):
    var_resp = await client.post(
        f"/api/v1/products/{TEST_PRODUCT_ID}/variants",
        json={"name": "Temp", "value": "Delete Me"},
    )
    variant_id = var_resp.json()["id"]

    resp = await client.delete(
        f"/api/v1/products/{TEST_PRODUCT_ID}/variants/{variant_id}"
    )

    assert resp.status_code == 204
