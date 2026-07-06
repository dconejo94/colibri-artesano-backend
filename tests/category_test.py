"""Tests for Categories CRUD endpoints."""

import uuid

from sqlalchemy import select

from app.domain.models.user import User
from tests.conftest import TestingSessionLocal
from tests.factories.product_factory import TEST_CATEGORY_ID, TEST_USER_ID


# ── Create ────────────────────────────────────────────────────────


async def _grant_admin_access():
    async with TestingSessionLocal() as db:
        user = (
            await db.execute(select(User).where(User.id == TEST_USER_ID))
        ).scalar_one()
        user.is_admin = True
        await db.commit()


async def test_create_category_requires_admin(client):
    body = {"name": "Ceramica", "slug": "ceramica"}
    resp = await client.post("/api/v1/categories/", json=body)

    assert resp.status_code == 403
    assert resp.json()["detail"] == "Se requiere rol de administrador."


async def test_create_category_success(client):
    await _grant_admin_access()
    body = {"name": "Ceramica", "slug": "ceramica"}
    resp = await client.post("/api/v1/categories/", json=body)

    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Ceramica"
    assert data["slug"] == "ceramica"
    assert "id" in data


async def test_create_category_duplicate_slug(client):
    await _grant_admin_access()
    body = {"name": "Artesania Dup", "slug": "artesania"}
    resp = await client.post("/api/v1/categories/", json=body)

    assert resp.status_code == 409


async def test_create_category_missing_fields(client):
    await _grant_admin_access()
    resp = await client.post("/api/v1/categories/", json={"name": "NoSlug"})

    assert resp.status_code == 422


# ── Read ──────────────────────────────────────────────────────────


async def test_list_categories(client):
    resp = await client.get("/api/v1/categories/")

    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1


async def test_get_category_by_id(client):
    resp = await client.get(f"/api/v1/categories/{TEST_CATEGORY_ID}")

    assert resp.status_code == 200
    assert resp.json()["id"] == str(TEST_CATEGORY_ID)


async def test_get_category_not_found(client):
    fake_id = uuid.uuid4()
    resp = await client.get(f"/api/v1/categories/{fake_id}")

    assert resp.status_code == 404


# ── Update ────────────────────────────────────────────────────────


async def test_update_category(client):
    await _grant_admin_access()
    resp = await client.put(
        f"/api/v1/categories/{TEST_CATEGORY_ID}",
        json={"name": "Updated Name"},
    )

    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated Name"
    assert resp.json()["slug"] == "artesania"


async def test_update_category_not_found(client):
    await _grant_admin_access()
    fake_id = uuid.uuid4()
    resp = await client.put(f"/api/v1/categories/{fake_id}", json={"name": "Nope"})

    assert resp.status_code == 404


# ── Delete ────────────────────────────────────────────────────────


async def test_delete_category(client):
    await _grant_admin_access()
    body = {"name": "ToDelete", "slug": "to-delete"}
    create_resp = await client.post("/api/v1/categories/", json=body)
    cat_id = create_resp.json()["id"]

    resp = await client.delete(f"/api/v1/categories/{cat_id}")
    assert resp.status_code == 204

    get_resp = await client.get(f"/api/v1/categories/{cat_id}")
    assert get_resp.status_code == 404


async def test_delete_category_not_found(client):
    await _grant_admin_access()
    fake_id = uuid.uuid4()
    resp = await client.delete(f"/api/v1/categories/{fake_id}")

    assert resp.status_code == 404
