"""Tests for event endpoints: listing, detail, creation and participation."""

import uuid
from datetime import datetime

from httpx import AsyncClient
from sqlalchemy import select

from app.domain.models.user import User
from app.domain.models.store import Store
from tests.conftest import TestingSessionLocal

_EVENTS = "/api/v1/events"
_REGISTER = "/api/v1/auth/register"
_LOGIN = "/api/v1/auth/login"


# ── Helpers ───────────────────────────────────────────────────────


def _event_payload(**overrides):
    payload = {
        "title": "Feria Artesanal",
        "description": "Encuentro cultural de artesanos",
        "location": "Bogotá",
        "latitude": 4.7110,
        "longitude": -74.0721,
        "event_date": "2026-07-01T10:00:00+00:00",
        "cover_image_url": "https://example.com/event.jpg",
    }
    payload.update(overrides)
    return payload

def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def _register_vendor(client: AsyncClient, email: str) -> str:
    resp = await client.post(
        _REGISTER,
        json={
            "email": email,
            "password": "password123",
            "role": "vendor",
            "store_name": f"Store {email}",
        },
    )
    return resp.json()["access_token"]


async def _register_buyer(client: AsyncClient, email: str) -> str:
    resp = await client.post(
        _REGISTER,
        json={"email": email, "password": "password123", "role": "buyer"},
    )
    return resp.json()["access_token"]


async def _make_admin(email: str) -> str:
    async with TestingSessionLocal() as db:
        user = (await db.execute(select(User).where(User.email == email))).scalar_one()
        user.is_admin = True
        await db.commit()
        return str(user.id)


async def _login(client: AsyncClient, email: str) -> str:
    resp = await client.post(_LOGIN, json={"email": email, "password": "password123"})
    return resp.json()["access_token"]


async def _create_admin(client: AsyncClient, email: str) -> str:
    await _register_buyer(client, email)
    await _make_admin(email)
    return await _login(client, email)


async def _create_event(client: AsyncClient, token: str, **overrides) -> dict:
    resp = await client.post(
        _EVENTS, json=_event_payload(**overrides), headers=_auth(token)
    )
    assert resp.status_code == 201
    return resp.json()


# ── Auth required ─────────────────────────────────────────────────


async def test_list_events_without_token_returns_401(auth_client: AsyncClient):
    resp = await auth_client.get(_EVENTS)
    assert resp.status_code == 401


async def test_get_event_without_token_returns_401(auth_client: AsyncClient):
    resp = await auth_client.get(f"{_EVENTS}/{uuid.uuid4()}")
    assert resp.status_code == 401


# ── Create (admin only) ───────────────────────────────────────────


async def test_create_event_as_admin(auth_client: AsyncClient):
    token = await _create_admin(auth_client, "admin_create@test.com")
    resp = await auth_client.post(_EVENTS, json=_event_payload(), headers=_auth(token))
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Feria Artesanal"
    assert data["participants"] == []
    assert data["my_participation"] is None


async def test_create_event_as_vendor_returns_403(auth_client: AsyncClient):
    token = await _register_vendor(auth_client, "vendor_403@test.com")
    resp = await auth_client.post(_EVENTS, json=_event_payload(), headers=_auth(token))
    assert resp.status_code == 403


async def test_create_event_as_buyer_returns_403(auth_client: AsyncClient):
    token = await _register_buyer(auth_client, "buyer_403@test.com")
    resp = await auth_client.post(_EVENTS, json=_event_payload(), headers=_auth(token))
    assert resp.status_code == 403


# ── Update (admin only) ───────────────────────────────────────────


async def test_update_event_as_admin(auth_client: AsyncClient):
    token = await _create_admin(auth_client, "admin_update@test.com")
    event = await _create_event(auth_client, token)

    resp = await auth_client.patch(
        f"{_EVENTS}/{event['id']}",
        json={"title": "Feria Actualizada"},
        headers=_auth(token),
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Feria Actualizada"


async def test_update_event_as_vendor_returns_403(auth_client: AsyncClient):
    admin_token = await _create_admin(auth_client, "admin_upd2@test.com")
    event = await _create_event(auth_client, admin_token)

    vendor_token = await _register_vendor(auth_client, "vendor_upd@test.com")
    resp = await auth_client.patch(
        f"{_EVENTS}/{event['id']}",
        json={"title": "Hack"},
        headers=_auth(vendor_token),
    )
    assert resp.status_code == 403


# ── Delete (admin only) ───────────────────────────────────────────


async def test_delete_event_as_admin(auth_client: AsyncClient):
    token = await _create_admin(auth_client, "admin_delete@test.com")
    event = await _create_event(auth_client, token)

    resp = await auth_client.delete(f"{_EVENTS}/{event['id']}", headers=_auth(token))
    assert resp.status_code == 204

    resp = await auth_client.get(f"{_EVENTS}/{event['id']}", headers=_auth(token))
    assert resp.status_code == 404


async def test_delete_event_as_vendor_returns_403(auth_client: AsyncClient):
    admin_token = await _create_admin(auth_client, "admin_del2@test.com")
    event = await _create_event(auth_client, admin_token)

    vendor_token = await _register_vendor(auth_client, "vendor_del@test.com")
    resp = await auth_client.delete(
        f"{_EVENTS}/{event['id']}", headers=_auth(vendor_token)
    )
    assert resp.status_code == 403


# ── List & detail ─────────────────────────────────────────────────


async def test_list_events_paginated(auth_client: AsyncClient):
    admin_token = await _create_admin(auth_client, "admin_list@test.com")
    await _create_event(auth_client, admin_token)

    buyer_token = await _register_buyer(auth_client, "buyer_list@test.com")
    resp = await auth_client.get(
        f"{_EVENTS}?page=1&limit=10", headers=_auth(buyer_token)
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["page"] == 1
    assert data["limit"] == 10
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


async def test_get_event_by_id(auth_client: AsyncClient):
    admin_token = await _create_admin(auth_client, "admin_detail@test.com")
    event = await _create_event(auth_client, admin_token)

    buyer_token = await _register_buyer(auth_client, "buyer_detail@test.com")
    resp = await auth_client.get(f"{_EVENTS}/{event['id']}", headers=_auth(buyer_token))
    assert resp.status_code == 200
    assert resp.json()["id"] == event["id"]


async def test_get_event_not_found(auth_client: AsyncClient):
    token = await _register_buyer(auth_client, "buyer_404@test.com")
    resp = await auth_client.get(f"{_EVENTS}/{uuid.uuid4()}", headers=_auth(token))
    assert resp.status_code == 404

async def test_list_upcoming_returns_only_future_events(auth_client: AsyncClient):
    admin_token = await _create_admin(auth_client, "admin_upcoming@test.com")

    await _create_event(
        auth_client,
        admin_token,
        title="Pasado",
        event_date="2020-01-01T10:00:00+00:00",
    )

    await _create_event(
        auth_client,
        admin_token,
        title="Futuro",
        event_date="2030-01-01T10:00:00+00:00",
    )

    buyer_token = await _register_buyer(auth_client, "buyer_upcoming@test.com")

    resp = await auth_client.get(
        f"{_EVENTS}/upcoming?page=1&limit=10",
        headers=_auth(buyer_token),
    )

    assert resp.status_code == 200

    titles = [e["title"] for e in resp.json()["items"]]

    assert "Futuro" in titles
    assert "Pasado" not in titles

async def test_list_nearby_returns_close_events(auth_client: AsyncClient):
    admin_token = await _create_admin(auth_client, "admin_near@test.com")

    await _create_event(
        auth_client,
        admin_token,
        title="San Jose",
        latitude=9.9281,
        longitude=-84.0907,
    )

    await _create_event(
        auth_client,
        admin_token,
        title="Muy lejos",
        latitude=40.7128,
        longitude=-74.0060,
    )

    buyer_token = await _register_buyer(auth_client, "buyer_near@test.com")

    resp = await auth_client.get(
        f"{_EVENTS}/nearby?lat=9.9281&lng=-84.0907&radius_km=10&page=1&limit=10",
        headers=_auth(buyer_token),
    )

    assert resp.status_code == 200

    titles = [e["title"] for e in resp.json()["items"]]

    assert "San Jose" in titles
    assert "Muy lejos" not in titles

async def test_create_event_invalid_latitude(auth_client: AsyncClient):
    token = await _create_admin(auth_client, "admin_lat@test.com")

    payload = _event_payload(latitude=200)

    resp = await auth_client.post(
        _EVENTS,
        json=payload,
        headers=_auth(token),
    )

    assert resp.status_code == 422

async def test_create_event_invalid_longitude(auth_client: AsyncClient):
    token = await _create_admin(auth_client, "admin_lng@test.com")

    payload = _event_payload(longitude=-300)

    resp = await auth_client.post(
        _EVENTS,
        json=payload,
        headers=_auth(token),
    )

    assert resp.status_code == 422

async def test_nearby_invalid_radius_too_small(auth_client: AsyncClient):
    token = await _register_buyer(auth_client, "buyer_radius1@test.com")

    resp = await auth_client.get(
        f"{_EVENTS}/nearby?lat=9.9&lng=-84.0&radius=0",
        headers=_auth(token),
    )

    assert resp.status_code == 422

async def test_nearby_invalid_radius_too_large(auth_client: AsyncClient):
    token = await _register_buyer(auth_client, "buyer_radius2@test.com")

    resp = await auth_client.get(
        f"{_EVENTS}/nearby?lat=9.9&lng=-84.0&radius=1000",
        headers=_auth(token),
    )

    assert resp.status_code == 422

async def test_nearby_returns_empty_when_no_events(auth_client: AsyncClient):
    buyer_token = await _register_buyer(auth_client, "buyer_empty@test.com")

    resp = await auth_client.get(
        f"{_EVENTS}/nearby?lat=9.9&lng=-84.0&radius_km=5&page=1&limit=10",
        headers=_auth(buyer_token),
    )

    assert resp.status_code == 200
    assert resp.json()["items"] == []

async def test_upcoming_pagination(auth_client: AsyncClient):
    admin_token = await _create_admin(auth_client, "admin_page@test.com")

    for i in range(3):
        await _create_event(
            auth_client,
            admin_token,
            title=f"Evento {i}",
            event_date=f"2030-01-0{i+1}T10:00:00+00:00",
        )

    buyer_token = await _register_buyer(auth_client, "buyer_page@test.com")

    resp = await auth_client.get(
        f"{_EVENTS}/upcoming?page=1&limit=2",
        headers=_auth(buyer_token),
    )

    assert resp.status_code == 200

    data = resp.json()

    assert data["page"] == 1
    assert data["limit"] == 2
    assert len(data["items"]) == 2
    assert data["total"] >= 3

# ── my_participation (vendor detail) ─────────────────────────────


async def test_vendor_sees_my_participation_null_when_not_requested(
    auth_client: AsyncClient,
):
    admin_token = await _create_admin(auth_client, "admin_myp@test.com")
    event = await _create_event(auth_client, admin_token)

    vendor_token = await _register_vendor(auth_client, "vendor_myp@test.com")
    resp = await auth_client.get(
        f"{_EVENTS}/{event['id']}", headers=_auth(vendor_token)
    )
    assert resp.status_code == 200
    assert resp.json()["my_participation"] is None


async def test_buyer_does_not_see_my_participation(auth_client: AsyncClient):
    admin_token = await _create_admin(auth_client, "admin_buyerp@test.com")
    event = await _create_event(auth_client, admin_token)

    buyer_token = await _register_buyer(auth_client, "buyer_myp@test.com")
    resp = await auth_client.get(f"{_EVENTS}/{event['id']}", headers=_auth(buyer_token))
    assert resp.status_code == 200
    assert resp.json()["my_participation"] is None


# ── Participation ─────────────────────────────────────────────────


async def test_vendor_can_request_participation(auth_client: AsyncClient):
    admin_token = await _create_admin(auth_client, "admin_part@test.com")
    event = await _create_event(auth_client, admin_token)

    vendor_token = await _register_vendor(auth_client, "vendor_part@test.com")
    resp = await auth_client.post(
        f"{_EVENTS}/{event['id']}/participants", headers=_auth(vendor_token)
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "pending"


async def test_vendor_cannot_request_participation_twice(auth_client: AsyncClient):
    admin_token = await _create_admin(auth_client, "admin_dup@test.com")
    event = await _create_event(auth_client, admin_token)

    vendor_token = await _register_vendor(auth_client, "vendor_dup@test.com")
    await auth_client.post(
        f"{_EVENTS}/{event['id']}/participants", headers=_auth(vendor_token)
    )
    resp = await auth_client.post(
        f"{_EVENTS}/{event['id']}/participants", headers=_auth(vendor_token)
    )
    assert resp.status_code == 409


async def test_buyer_cannot_request_participation(auth_client: AsyncClient):
    admin_token = await _create_admin(auth_client, "admin_bpart@test.com")
    event = await _create_event(auth_client, admin_token)

    buyer_token = await _register_buyer(auth_client, "buyer_part@test.com")
    resp = await auth_client.post(
        f"{_EVENTS}/{event['id']}/participants", headers=_auth(buyer_token)
    )
    assert resp.status_code == 403


async def test_vendor_can_withdraw_participation(auth_client: AsyncClient):
    admin_token = await _create_admin(auth_client, "admin_with@test.com")
    event = await _create_event(auth_client, admin_token)

    vendor_token = await _register_vendor(auth_client, "vendor_with@test.com")
    await auth_client.post(
        f"{_EVENTS}/{event['id']}/participants", headers=_auth(vendor_token)
    )

    async with TestingSessionLocal() as db:
        store = (
            await db.execute(
                select(Store)
                .join(User, Store.owner_id == User.id)
                .where(User.email == "vendor_with@test.com")
            )
        ).scalar_one()
        store_id = store.id

    resp = await auth_client.delete(
        f"{_EVENTS}/{event['id']}/participants/{store_id}",
        headers=_auth(vendor_token),
    )
    assert resp.status_code == 204


async def test_vendor_cannot_withdraw_foreign_store(auth_client: AsyncClient):
    admin_token = await _create_admin(auth_client, "admin_idor@test.com")
    event = await _create_event(auth_client, admin_token)

    vendor1_token = await _register_vendor(auth_client, "vendor_idor1@test.com")
    await auth_client.post(
        f"{_EVENTS}/{event['id']}/participants", headers=_auth(vendor1_token)
    )

    async with TestingSessionLocal() as db:
        store = (
            await db.execute(
                select(Store)
                .join(User, Store.owner_id == User.id)
                .where(User.email == "vendor_idor1@test.com")
            )
        ).scalar_one()
        store_id = store.id

    vendor2_token = await _register_vendor(auth_client, "vendor_idor2@test.com")
    resp = await auth_client.delete(
        f"{_EVENTS}/{event['id']}/participants/{store_id}",
        headers=_auth(vendor2_token),
    )
    assert resp.status_code == 403


async def test_admin_can_list_participants(auth_client: AsyncClient):
    admin_token = await _create_admin(auth_client, "admin_lpart@test.com")
    event = await _create_event(auth_client, admin_token)

    vendor_token = await _register_vendor(auth_client, "vendor_lpart@test.com")
    await auth_client.post(
        f"{_EVENTS}/{event['id']}/participants", headers=_auth(vendor_token)
    )

    resp = await auth_client.get(
        f"{_EVENTS}/{event['id']}/participants", headers=_auth(admin_token)
    )
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


async def test_vendor_cannot_list_participants(auth_client: AsyncClient):
    admin_token = await _create_admin(auth_client, "admin_vlpart@test.com")
    event = await _create_event(auth_client, admin_token)

    vendor_token = await _register_vendor(auth_client, "vendor_vlpart@test.com")
    resp = await auth_client.get(
        f"{_EVENTS}/{event['id']}/participants", headers=_auth(vendor_token)
    )
    assert resp.status_code == 403


async def test_admin_can_approve_participation(auth_client: AsyncClient):
    admin_token = await _create_admin(auth_client, "admin_approve@test.com")
    event = await _create_event(auth_client, admin_token)

    vendor_token = await _register_vendor(auth_client, "vendor_approve@test.com")
    await auth_client.post(
        f"{_EVENTS}/{event['id']}/participants", headers=_auth(vendor_token)
    )

    async with TestingSessionLocal() as db:
        store = (
            await db.execute(
                select(Store)
                .join(User, Store.owner_id == User.id)
                .where(User.email == "vendor_approve@test.com")
            )
        ).scalar_one()
        store_id = store.id

    resp = await auth_client.patch(
        f"{_EVENTS}/{event['id']}/participants/{store_id}",
        json={"status": "approved"},
        headers=_auth(admin_token),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "approved"


async def test_approved_store_appears_in_event_feed(auth_client: AsyncClient):
    admin_token = await _create_admin(auth_client, "admin_feed@test.com")
    event = await _create_event(auth_client, admin_token)

    vendor_token = await _register_vendor(auth_client, "vendor_feed@test.com")
    await auth_client.post(
        f"{_EVENTS}/{event['id']}/participants", headers=_auth(vendor_token)
    )

    async with TestingSessionLocal() as db:
        store = (
            await db.execute(
                select(Store)
                .join(User, Store.owner_id == User.id)
                .where(User.email == "vendor_feed@test.com")
            )
        ).scalar_one()
        store_id = store.id

    await auth_client.patch(
        f"{_EVENTS}/{event['id']}/participants/{store_id}",
        json={"status": "approved"},
        headers=_auth(admin_token),
    )

    buyer_token = await _register_buyer(auth_client, "buyer_feed@test.com")
    resp = await auth_client.get(f"{_EVENTS}/{event['id']}", headers=_auth(buyer_token))
    assert resp.status_code == 200
    participants = resp.json()["participants"]
    assert any(str(p["id"]) == str(store_id) for p in participants)


async def test_pending_store_not_in_public_feed(auth_client: AsyncClient):
    admin_token = await _create_admin(auth_client, "admin_pending@test.com")
    event = await _create_event(auth_client, admin_token)

    vendor_token = await _register_vendor(auth_client, "vendor_pending@test.com")
    await auth_client.post(
        f"{_EVENTS}/{event['id']}/participants", headers=_auth(vendor_token)
    )

    buyer_token = await _register_buyer(auth_client, "buyer_pending@test.com")
    resp = await auth_client.get(f"{_EVENTS}/{event['id']}", headers=_auth(buyer_token))
    assert resp.status_code == 200
    assert resp.json()["participants"] == []


async def test_vendor_sees_my_participation_after_request(auth_client: AsyncClient):
    admin_token = await _create_admin(auth_client, "admin_myp2@test.com")
    event = await _create_event(auth_client, admin_token)

    vendor_token = await _register_vendor(auth_client, "vendor_myp2@test.com")
    await auth_client.post(
        f"{_EVENTS}/{event['id']}/participants", headers=_auth(vendor_token)
    )

    resp = await auth_client.get(
        f"{_EVENTS}/{event['id']}", headers=_auth(vendor_token)
    )
    assert resp.status_code == 200
    assert resp.json()["my_participation"] == "pending"


# ── DateTime validation ───────────────────────────────────────────


async def test_create_event_without_event_date_returns_422(auth_client: AsyncClient):
    token = await _create_admin(auth_client, "admin_nodate@test.com")
    payload = _event_payload()
    del payload["event_date"]
    resp = await auth_client.post(_EVENTS, json=payload, headers=_auth(token))
    assert resp.status_code == 422


async def test_create_event_dates_preserve_timezone(auth_client: AsyncClient):
    token = await _create_admin(auth_client, "admin_tz@test.com")
    resp = await auth_client.post(_EVENTS, json=_event_payload(), headers=_auth(token))
    assert resp.status_code == 201
    event_date = datetime.fromisoformat(resp.json()["event_date"])
    assert event_date.tzinfo is not None
