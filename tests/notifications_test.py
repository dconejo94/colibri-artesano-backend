import uuid
from tests.factories.product_factory import (
    TEST_PRODUCT_ID,
    TEST_NOTIFICATION_ID2,
    TEST_NOTIFICATION_ID,
    TEST_NOTIFICATION_ID3,
)

# ── GET /notifications/ ───────────────────────────────────────────


async def test_get_notifications_returns_own(client):
    resp = await client.get("/api/v1/notifications/")

    assert resp.status_code == 200
    assert resp.json()["total"] == 2


async def test_get_notifications_does_not_return_others(client):
    resp = await client.get("/api/v1/notifications/")

    data = resp.json()
    returned_ids = {n["id"] for n in data["items"]}

    assert str(TEST_NOTIFICATION_ID) in returned_ids
    assert str(TEST_NOTIFICATION_ID2) in returned_ids

    assert str(TEST_NOTIFICATION_ID3) not in returned_ids


async def test_get_notifications_response_schema(client):
    resp = await client.get("/api/v1/notifications/")

    item = resp.json()["items"][0]

    assert "id" in item
    assert "title" in item
    assert "body" in item
    assert "type" in item
    assert "is_read" in item
    assert "created_at" in item


async def test_get_notifications_pagination(client):
    resp = await client.get("/api/v1/notifications/?page=1&limit=1")

    data = resp.json()

    assert data["total"] == 2
    assert len(data["items"]) == 1


# ── GET /notifications/unread ─────────────────────────────────────


async def test_get_unread_notifications(client):
    resp = await client.get("/api/v1/notifications/unread")

    data = resp.json()

    assert data["total"] == 1
    assert all(item["is_read"] is False for item in data["items"])


# ── PATCH /notifications/{id}/read ───────────────────────────────


async def test_mark_notification_as_read(client):
    notif_id = str(TEST_NOTIFICATION_ID)

    resp = await client.patch(f"/api/v1/notifications/{notif_id}/read")

    assert resp.status_code == 204


async def test_mark_notification_as_read_reflects_on_get(client):
    notif_id = str(TEST_NOTIFICATION_ID)

    await client.patch(f"/api/v1/notifications/{notif_id}/read")

    resp = await client.get("/api/v1/notifications/")
    data = resp.json()

    item = next(i for i in data["items"] if i["id"] == notif_id)

    assert item["is_read"] is True


async def test_mark_notification_not_found(client):
    resp = await client.patch(f"/api/v1/notifications/{uuid.uuid4()}/read")

    assert resp.status_code == 404


async def test_mark_other_users_notification_returns_404(client):
    resp = await client.patch(f"/api/v1/notifications/{TEST_NOTIFICATION_ID3}/read")

    assert resp.status_code == 404


# ── POST /notifications/token ─────────────────────────────────────


async def test_register_fcm_token(client):
    resp = await client.post(
        "/api/v1/notifications/token",
        json={"token": "fcm-test-token-abc123"},
    )

    assert resp.status_code == 204


async def test_register_fcm_token_missing_body(client):
    resp = await client.post("/api/v1/notifications/token", json={})

    assert resp.status_code == 422


# ── Triggers ─────────────────────────────────────────────────────


async def test_checkout_creates_order_confirmed_notification(client):
    from tests.factories.product_factory import TEST_VARIANT_1_ID

    await client.post(
        "/api/v1/cart/item",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "variant_id": str(TEST_VARIANT_1_ID),
            "quantity": 1,
        },
    )
    await client.post("/api/v1/orders/")

    resp = await client.get("/api/v1/notifications/")

    data = resp.json()

    assert any(n["type"] == "order_confirmed" for n in data["items"])
