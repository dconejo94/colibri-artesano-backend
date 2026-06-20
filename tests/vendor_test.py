"""Tests for vendor profile endpoint and role-based access control (RBAC + IDOR)."""

import uuid

import pytest
from httpx import AsyncClient

from tests.factories.product_factory import TEST_STORE_ID


# ---------------------------------------------------------------------------
# Profile endpoint — canonical path
# ---------------------------------------------------------------------------


async def test_get_store_profile(client: AsyncClient):
    """New canonical endpoint: GET /stores/{store_id}/profile."""
    resp = await client.get(f"/api/v1/stores/{TEST_STORE_ID}/profile")

    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(TEST_STORE_ID)
    assert data["name"] == "Test Store"
    assert data["product_count"] == 2


async def test_get_store_profile_not_found(client: AsyncClient):
    resp = await client.get(f"/api/v1/stores/{uuid.uuid4()}/profile")

    assert resp.status_code == 404


async def test_get_store_profile_does_not_expose_owner_id(client: AsyncClient):
    """The profile DTO must not leak owner_id."""
    resp = await client.get(f"/api/v1/stores/{TEST_STORE_ID}/profile")

    assert "owner_id" not in resp.json()


# ---------------------------------------------------------------------------
# Legacy /vendors/ route — deprecated but still functional
# ---------------------------------------------------------------------------


async def test_get_vendor_profile_legacy_still_works(client: AsyncClient):
    """The old /vendors/{store_id} path must remain 200 during transition."""
    resp = await client.get(f"/api/v1/vendors/{TEST_STORE_ID}")

    assert resp.status_code == 200
    assert resp.json()["name"] == "Test Store"


async def test_get_vendor_not_found_legacy(client: AsyncClient):
    resp = await client.get(f"/api/v1/vendors/{uuid.uuid4()}")

    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Role check — only vendors can access write endpoints
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "method,path,body",
    [
        ("POST", "/api/v1/stores/", {"owner_id": str(uuid.uuid4()), "name": "X"}),
        ("PUT", f"/api/v1/stores/{TEST_STORE_ID}", {"name": "X"}),
        ("DELETE", f"/api/v1/stores/{TEST_STORE_ID}", None),
        (
            "POST",
            f"/api/v1/stores/{TEST_STORE_ID}/products",
            {"name": "P", "base_price": "1.00"},
        ),
        ("GET", f"/api/v1/stores/{TEST_STORE_ID}/orders", None),
    ],
)
async def test_vendor_only_endpoints_forbidden_for_buyer(
    client: AsyncClient, method, path, body
):
    from app.main import app
    from app.core.security import get_current_user
    from app.domain.models.user import User

    buyer = User(
        id=uuid.UUID("00000000-0000-0000-0000-000000000099"),
        email="buyer@test.com",
        password_hash="hash",
        is_active=True,
        role="buyer",
    )

    async def override_buyer():
        return buyer

    app.dependency_overrides[get_current_user] = override_buyer

    try:
        if method == "POST":
            resp = await client.post(path, json=body)
        elif method == "PUT":
            resp = await client.put(path, json=body)
        elif method == "DELETE":
            resp = await client.delete(path)
        else:
            resp = await client.get(path)
    finally:
        del app.dependency_overrides[get_current_user]

    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# IDOR / ownership check — vendor cannot mutate another vendor's store
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "method,path,body",
    [
        ("PUT", f"/api/v1/stores/{TEST_STORE_ID}", {"name": "Stolen"}),
        ("DELETE", f"/api/v1/stores/{TEST_STORE_ID}", None),
        (
            "POST",
            f"/api/v1/stores/{TEST_STORE_ID}/products",
            {"name": "P", "base_price": "1.00"},
        ),
        ("GET", f"/api/v1/stores/{TEST_STORE_ID}/orders", None),
    ],
)
async def test_vendor_cannot_mutate_another_vendors_store(
    client: AsyncClient, method, path, body
):
    """A legitimate vendor with the correct role but a different store must
    receive 403 on any write/read-restricted operation on another vendor's store.
    This is the IDOR (horizontal privilege escalation) guard.
    """
    from app.main import app
    from app.core.security import get_current_user
    from app.domain.models.user import User

    other_vendor = User(
        id=uuid.UUID("00000000-0000-0000-0000-000000000088"),  # NOT the store owner
        email="other@test.com",
        password_hash="hash",
        is_active=True,
        role="vendor",
    )

    async def override_other_vendor():
        return other_vendor

    app.dependency_overrides[get_current_user] = override_other_vendor

    try:
        if method == "POST":
            resp = await client.post(path, json=body)
        elif method == "PUT":
            resp = await client.put(path, json=body)
        elif method == "DELETE":
            resp = await client.delete(path)
        else:
            resp = await client.get(path)
    finally:
        del app.dependency_overrides[get_current_user]

    assert resp.status_code == 403, (
        f"Expected 403 for {method} {path} by a non-owner vendor, got {resp.status_code}"
    )
