"""Tests for vendor profile endpoint and role-based access control."""

import uuid

import pytest
from httpx import AsyncClient

from tests.factories.product_factory import TEST_STORE_ID


async def test_get_vendor_profile(client: AsyncClient):
    resp = await client.get(f"/api/v1/vendors/{TEST_STORE_ID}")

    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(TEST_STORE_ID)
    assert data["name"] == "Test Store"
    assert data["product_count"] == 1


async def test_get_vendor_not_found(client: AsyncClient):
    resp = await client.get(f"/api/v1/vendors/{uuid.uuid4()}")

    assert resp.status_code == 404


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
