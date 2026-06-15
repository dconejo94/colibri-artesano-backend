"""Tests for the auth endpoints: register, login, refresh and route protection."""

from sqlalchemy import select

from app.domain.models.store import Store
from app.domain.models.user import User
from tests.conftest import TestingSessionLocal

_REGISTER = "/api/v1/auth/register"
_LOGIN = "/api/v1/auth/login"
_REFRESH = "/api/v1/auth/refresh"


def _buyer(email="buyer1@test.com", password="password123"):
    return {"email": email, "password": password, "role": "buyer"}


# ── Register ──────────────────────────────────────────────────────


async def test_register_buyer_returns_tokens(client):
    resp = await client.post(_REGISTER, json=_buyer())
    assert resp.status_code == 201
    data = resp.json()
    assert data["access_token"] and data["refresh_token"]
    assert data["token_type"] == "bearer"


async def test_register_vendor_creates_store(client):
    payload = {
        "email": "vendor1@test.com",
        "password": "password123",
        "role": "vendor",
        "store_name": "Vendor One Store",
    }
    resp = await client.post(_REGISTER, json=payload)
    assert resp.status_code == 201

    async with TestingSessionLocal() as db:
        user = (
            await db.execute(select(User).where(User.email == "vendor1@test.com"))
        ).scalar_one()
        store = (
            await db.execute(select(Store).where(Store.owner_id == user.id))
        ).scalar_one_or_none()
    assert store is not None
    assert store.name == "Vendor One Store"


async def test_register_duplicate_email_returns_409(client):
    await client.post(_REGISTER, json=_buyer(email="dup@test.com"))
    resp = await client.post(_REGISTER, json=_buyer(email="dup@test.com"))
    assert resp.status_code == 409


async def test_register_vendor_without_store_name_returns_422(client):
    payload = {"email": "v2@test.com", "password": "password123", "role": "vendor"}
    resp = await client.post(_REGISTER, json=payload)
    assert resp.status_code == 422


async def test_register_short_password_returns_422(client):
    resp = await client.post(_REGISTER, json=_buyer(password="short"))
    assert resp.status_code == 422


async def test_register_invalid_email_returns_422(client):
    resp = await client.post(_REGISTER, json=_buyer(email="not-an-email"))
    assert resp.status_code == 422


# ── Login ─────────────────────────────────────────────────────────


async def test_login_success(client):
    await client.post(_REGISTER, json=_buyer(email="login@test.com"))
    resp = await client.post(
        _LOGIN, json={"email": "login@test.com", "password": "password123"}
    )
    assert resp.status_code == 200
    assert resp.json()["access_token"]


async def test_login_wrong_password_returns_401(client):
    await client.post(_REGISTER, json=_buyer(email="wp@test.com"))
    resp = await client.post(
        _LOGIN, json={"email": "wp@test.com", "password": "wrong-password"}
    )
    assert resp.status_code == 401


async def test_login_unknown_email_returns_401(client):
    resp = await client.post(
        _LOGIN, json={"email": "nobody@test.com", "password": "password123"}
    )
    assert resp.status_code == 401


# ── Refresh ───────────────────────────────────────────────────────


async def test_refresh_returns_new_access_token(client):
    tokens = (await client.post(_REGISTER, json=_buyer(email="r@test.com"))).json()
    resp = await client.post(_REFRESH, json={"refresh_token": tokens["refresh_token"]})
    assert resp.status_code == 200
    assert resp.json()["access_token"]


async def test_refresh_rejects_access_token(client):
    tokens = (await client.post(_REGISTER, json=_buyer(email="r2@test.com"))).json()
    # An access token must not be usable as a refresh token.
    resp = await client.post(_REFRESH, json={"refresh_token": tokens["access_token"]})
    assert resp.status_code == 401


async def test_refresh_invalid_token_returns_401(client):
    resp = await client.post(_REFRESH, json={"refresh_token": "not-a-jwt"})
    assert resp.status_code == 401


# ── Real route protection (no seed-user override) ─────────────────


async def test_protected_route_without_token_returns_401(auth_client):
    resp = await auth_client.get("/api/v1/users/me")
    assert resp.status_code == 401


async def test_protected_route_with_token_succeeds(auth_client):
    tokens = (
        await auth_client.post(_REGISTER, json=_buyer(email="me@test.com"))
    ).json()
    resp = await auth_client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert resp.status_code == 200
    assert resp.json()["email"] == "me@test.com"
