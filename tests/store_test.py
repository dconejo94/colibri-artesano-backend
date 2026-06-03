"""Tests for Stores CRUD endpoints."""

import uuid

from tests.factories.product_factory import (
    TEST_USER_ID,
    TEST_STORE_ID,
)


# ── Create ────────────────────────────────────────────────────────


async def test_create_store_duplicate_owner(client):
    """User already has a store → 409."""
    body = {
        "owner_id": str(TEST_USER_ID),
        "name": "Second Store",
    }
    resp = await client.post("/api/v1/stores/", json=body)

    assert resp.status_code == 409


async def test_create_store_missing_name(client):
    resp = await client.post(
        "/api/v1/stores/",
        json={"owner_id": str(TEST_USER_ID)},
    )

    assert resp.status_code == 422


# ── Read ──────────────────────────────────────────────────────────


async def test_list_stores(client):
    resp = await client.get("/api/v1/stores/")

    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


async def test_get_store_by_id(client):
    resp = await client.get(f"/api/v1/stores/{TEST_STORE_ID}")

    assert resp.status_code == 200
    assert resp.json()["name"] == "Test Store"


async def test_get_store_not_found(client):
    fake_id = uuid.uuid4()
    resp = await client.get(f"/api/v1/stores/{fake_id}")

    assert resp.status_code == 404


# ── Update ────────────────────────────────────────────────────────


async def test_update_store(client):
    resp = await client.put(
        f"/api/v1/stores/{TEST_STORE_ID}",
        json={"name": "Renamed Store"},
    )

    assert resp.status_code == 200
    assert resp.json()["name"] == "Renamed Store"


async def test_update_store_not_found(client):
    fake_id = uuid.uuid4()
    resp = await client.put(f"/api/v1/stores/{fake_id}", json={"name": "Ghost"})

    assert resp.status_code == 404


# ── Delete ────────────────────────────────────────────────────────


async def test_delete_store_not_found(client):
    fake_id = uuid.uuid4()
    resp = await client.delete(f"/api/v1/stores/{fake_id}")

    assert resp.status_code == 404
