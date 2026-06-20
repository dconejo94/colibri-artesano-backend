import uuid
from decimal import Decimal

from tests.factories.product_factory import TEST_PRODUCT_ID, TEST_VARIANT_1_ID, TEST_VARIANT_2_ID


async def test_add_product_success(client):
    resp = await client.post(
        "/api/v1/cart/item",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "quantity": 1,
        },
    )

    assert resp.status_code == 201

    data = resp.json()

    assert len(data["stores"]) == 1
    assert len(data["stores"][0]["items"]) == 1


async def test_add_nonexistent_product_returns_404(client):
    resp = await client.post(
        "/api/v1/cart/item",
        json={
            "product_id": str(uuid.uuid4()),
            "quantity": 1,
        },
    )

    assert resp.status_code == 404


async def test_add_same_product_twice_accumulates_quantity(client):
    await client.post(
        "/api/v1/cart/item",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "quantity": 2,
        },
    )

    resp = await client.post(
        "/api/v1/cart/item",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "quantity": 3,
        },
    )

    assert resp.status_code == 201

    data = resp.json()

    item = data["stores"][0]["items"][0]

    assert item["quantity"] == 5

async def test_add_product_with_variant_success(client):
    resp = await client.post(
        "/api/v1/cart/item",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "variant_id": str(TEST_VARIANT_1_ID),
            "quantity": 1,
        },
    )

    assert resp.status_code == 201

    item = resp.json()["stores"][0]["items"][0]

    assert item["variant_id"] == str(TEST_VARIANT_1_ID)
    assert item["variant_name"] == "Size"
    assert item["variant_value"] == "S"

async def test_add_product_with_variant_uses_variant_price(client):
    resp = await client.post(
        "/api/v1/cart/item",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "variant_id": str(TEST_VARIANT_2_ID),
            "quantity": 1,
        },
    )

    item = resp.json()["stores"][0]["items"][0]

    assert Decimal(item["unit_price"]) == Decimal("15.00")

async def test_add_same_variant_twice_accumulates_quantity(client):
    await client.post(
        "/api/v1/cart/item",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "variant_id": str(TEST_VARIANT_1_ID),
            "quantity": 2,
        },
    )

    resp = await client.post(
        "/api/v1/cart/item",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "variant_id": str(TEST_VARIANT_1_ID),
            "quantity": 3,
        },
    )
    
    item = resp.json()["stores"][0]["items"][0]

    assert item["quantity"] == 5

async def test_different_variants_create_separate_cart_items(client):
    await client.post(
        "/api/v1/cart/item",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "variant_id": str(TEST_VARIANT_1_ID),
            "quantity": 2,
        },
    )

    resp = await client.post(
        "/api/v1/cart/item",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "variant_id": str(TEST_VARIANT_2_ID),
            "quantity": 1,
        },
    )

    items = resp.json()["stores"][0]["items"]

    assert len(items) == 2

    variant_ids = {item["variant_id"] for item in items}

    assert str(TEST_VARIANT_1_ID) in variant_ids
    assert str(TEST_VARIANT_2_ID) in variant_ids