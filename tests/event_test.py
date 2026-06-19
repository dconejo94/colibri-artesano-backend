"""Tests for event endpoints: listing, detail, creation."""

import uuid
from datetime import datetime
from httpx import AsyncClient
from sqlalchemy import select

from app.domain.models.user import User
from app.main import app
from app.core.security import get_current_user
from tests.conftest import TestingSessionLocal

_EVENTS = "/api/v1/events"
_REGISTER = "/api/v1/auth/register"


def _event_payload(**overrides):
    payload = {
        "title": "Feria Artesanal",
        "description": "Encuentro cultural de artesanos",
        "location": "Bogotá",
        "start_at": "2026-07-01T10:00:00+00:00",
        "end_at": "2026-07-01T18:00:00+00:00",
        "image_url": "https://example.com/event.jpg",
    }
    payload.update(overrides)
    return payload


async def _register_vendor(client: AsyncClient, email: str):
    return await client.post(
        _REGISTER,
        json={
            "email": email,
            "password": "password123",
            "role": "vendor",
            "store_name": f"Store {email}",
        },
    )


async def _register_buyer(client: AsyncClient, email: str):
    return await client.post(
        _REGISTER,
        json={"email": email, "password": "password123", "role": "buyer"},
    )


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def _create_event(auth_client: AsyncClient, token: str) -> dict:
    resp = await auth_client.post(_EVENTS, json=_event_payload(), headers=_auth(token))
    assert resp.status_code == 201
    return resp.json()


# ── Auth required ─────────────────────────────────────────────────


async def test_list_events_without_token_returns_401(auth_client: AsyncClient):
    resp = await auth_client.get(_EVENTS)
    assert resp.status_code == 401


async def test_get_event_without_token_returns_401(auth_client: AsyncClient):
    resp = await auth_client.get(f"{_EVENTS}/{uuid.uuid4()}")
    assert resp.status_code == 401


# ── Create (vendor/admin only) ────────────────────────────────────


async def test_create_event_as_vendor(auth_client: AsyncClient):
    reg = await _register_vendor(auth_client, "eventvendor@test.com")
    token = reg.json()["access_token"]

    resp = await auth_client.post(_EVENTS, json=_event_payload(), headers=_auth(token))
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Feria Artesanal"


async def test_create_event_as_admin(auth_client: AsyncClient):
    await _register_buyer(auth_client, "adminbuyer@test.com")
    async with TestingSessionLocal() as db:
        user = (
            await db.execute(select(User).where(User.email == "adminbuyer@test.com"))
        ).scalar_one()
        user.is_admin = True
        await db.commit()

    login = await auth_client.post(
        "/api/v1/auth/login",
        json={"email": "adminbuyer@test.com", "password": "password123"},
    )
    token = login.json()["access_token"]

    resp = await auth_client.post(
        _EVENTS, json=_event_payload(title="Admin Event"), headers=_auth(token)
    )
    assert resp.status_code == 201


async def test_create_event_as_buyer_returns_403(client: AsyncClient):
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
        resp = await client.post(_EVENTS, json=_event_payload())
    finally:
        del app.dependency_overrides[get_current_user]

    assert resp.status_code == 403


# ── List & detail ─────────────────────────────────────────────────


async def test_list_events_paginated(auth_client: AsyncClient):
    reg = await _register_vendor(auth_client, "listvendor@test.com")
    token = reg.json()["access_token"]
    await _create_event(auth_client, token)

    resp = await auth_client.get(f"{_EVENTS}?page=1&limit=10", headers=_auth(token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["page"] == 1
    assert data["limit"] == 10
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


async def test_get_event_by_id(auth_client: AsyncClient):
    reg = await _register_vendor(auth_client, "detailvendor@test.com")
    token = reg.json()["access_token"]
    created = await _create_event(auth_client, token)

    resp = await auth_client.get(f"{_EVENTS}/{created['id']}", headers=_auth(token))
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


async def test_get_event_not_found(auth_client: AsyncClient):
    reg = await _register_buyer(auth_client, "notfound@test.com")
    token = reg.json()["access_token"]

    resp = await auth_client.get(f"{_EVENTS}/{uuid.uuid4()}", headers=_auth(token))
    assert resp.status_code == 404

    # ── DateTime validation ───────────────────────────────────────────


async def test_create_event_without_start_at_returns_422(auth_client: AsyncClient):
    reg = await _register_vendor(auth_client, "nostart@test.com")
    token = reg.json()["access_token"]

    payload = _event_payload()
    del payload["start_at"]

    resp = await auth_client.post(_EVENTS, json=payload, headers=_auth(token))
    assert resp.status_code == 422


async def test_create_event_dates_preserve_timezone(auth_client: AsyncClient):
    reg = await _register_vendor(auth_client, "tzvendor@test.com")
    token = reg.json()["access_token"]

    resp = await auth_client.post(_EVENTS, json=_event_payload(), headers=_auth(token))
    assert resp.status_code == 201
    data = resp.json()

    start_at = datetime.fromisoformat(data["start_at"])
    end_at = datetime.fromisoformat(data["end_at"])

    assert start_at.tzinfo is not None
    assert end_at.tzinfo is not None


async def test_create_event_end_at_before_start_at_returns_422(
    auth_client: AsyncClient,
):
    reg = await _register_vendor(auth_client, "dateorder@test.com")
    token = reg.json()["access_token"]

    payload = _event_payload(
        start_at="2026-07-01T18:00:00+00:00",
        end_at="2026-07-01T10:00:00+00:00",
    )

    resp = await auth_client.post(_EVENTS, json=payload, headers=_auth(token))
    assert resp.status_code == 422
