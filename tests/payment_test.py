"""Tests for Stripe payments: create-intent ties a PaymentIntent to the
buyer's cart, and the webhook verifies signatures and updates payment_status.
The Stripe API is mocked; webhook signatures are real HMACs so the
verification code path runs for real.
"""

import hashlib
import hmac
import json
import time
import uuid

import pytest
import stripe
from sqlalchemy import select

from app.config import settings
from app.domain.models.main_order import MainOrder
from tests.conftest import TestingSessionLocal
from tests.factories.product_factory import TEST_PRODUCT_ID, TEST_VARIANT_1_ID

TEST_SECRET_KEY = "sk_test_dummy"
TEST_WEBHOOK_SECRET = "whsec_test_dummy"


class FakeIntent:
    def __init__(self, intent_id="pi_test_123"):
        self.id = intent_id
        self.client_secret = f"{intent_id}_secret_abc"


@pytest.fixture
def stripe_configured(monkeypatch):
    """Set dummy Stripe keys and capture PaymentIntent.create_async calls."""
    monkeypatch.setattr(settings, "STRIPE_SECRET_KEY", TEST_SECRET_KEY)
    monkeypatch.setattr(settings, "STRIPE_WEBHOOK_SECRET", TEST_WEBHOOK_SECRET)

    captured = {}

    async def fake_create_async(**kwargs):
        captured.update(kwargs)
        return FakeIntent()

    monkeypatch.setattr(stripe.PaymentIntent, "create_async", fake_create_async)
    return captured


async def _add_to_cart(client, quantity=2):
    resp = await client.post(
        "/api/v1/cart/item",
        json={
            "product_id": str(TEST_PRODUCT_ID),
            "variant_id": str(TEST_VARIANT_1_ID),
            "quantity": quantity,
        },
    )
    assert resp.status_code == 201


async def _get_cart_order():
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(MainOrder).where(MainOrder.status == "cart")
        )
        return result.scalars().first()


def _sign(payload: bytes, secret: str) -> str:
    """Build a real Stripe-Signature header (t=...,v1=HMAC-SHA256)."""
    timestamp = int(time.time())
    signed = f"{timestamp}.".encode() + payload
    digest = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={digest}"


def _intent_event(event_type: str, order_id: str, intent_id="pi_test_123") -> bytes:
    event = {
        "id": "evt_test_1",
        "object": "event",
        "type": event_type,
        "data": {
            "object": {
                "id": intent_id,
                "object": "payment_intent",
                "metadata": {"order_id": order_id},
            }
        },
    }
    return json.dumps(event).encode()


async def _post_webhook(client, payload: bytes, secret=TEST_WEBHOOK_SECRET):
    return await client.post(
        "/api/v1/payments/webhook",
        content=payload,
        headers={"stripe-signature": _sign(payload, secret)},
    )


# ── create-intent ─────────────────────────────────────────────────


async def test_create_intent_returns_camelcase_response(client, stripe_configured):
    await _add_to_cart(client, quantity=2)

    resp = await client.post("/api/v1/payments/create-intent")

    assert resp.status_code == 200
    data = resp.json()
    # The mobile client expects exactly these camelCase keys.
    assert data == {
        "clientSecret": "pi_test_123_secret_abc",
        "paymentIntentId": "pi_test_123",
    }


async def test_create_intent_charges_cart_total_in_minor_units(
    client, stripe_configured
):
    # 2 x 10.00 = 20.00 -> 2000 cents
    await _add_to_cart(client, quantity=2)

    resp = await client.post("/api/v1/payments/create-intent")

    assert resp.status_code == 200
    assert stripe_configured["amount"] == 2000
    assert stripe_configured["currency"] == "usd"

    cart = await _get_cart_order()
    assert stripe_configured["metadata"] == {"order_id": str(cart.id)}
    # Same cart + same amount must reuse the intent on Stripe's side.
    assert stripe_configured["idempotency_key"] == f"cart-{cart.id}-2000"


async def test_create_intent_stores_payment_reference_on_cart(
    client, stripe_configured
):
    await _add_to_cart(client)

    resp = await client.post("/api/v1/payments/create-intent")

    assert resp.status_code == 200
    cart = await _get_cart_order()
    assert cart.payment_reference == "pi_test_123"
    assert cart.payment_method == "card"
    assert cart.payment_status == "pending"


async def test_create_intent_empty_cart_returns_409(client, stripe_configured):
    resp = await client.post("/api/v1/payments/create-intent")

    assert resp.status_code == 409


async def test_create_intent_without_stripe_key_returns_503(client):
    # Default settings leave STRIPE_SECRET_KEY empty.
    await _add_to_cart(client)

    resp = await client.post("/api/v1/payments/create-intent")

    assert resp.status_code == 503


# ── webhook ───────────────────────────────────────────────────────


async def test_webhook_succeeded_updates_payment_status(client, stripe_configured):
    await _add_to_cart(client)
    cart = await _get_cart_order()

    payload = _intent_event("payment_intent.succeeded", str(cart.id))
    resp = await _post_webhook(client, payload)

    assert resp.status_code == 200
    updated = await _get_cart_order()
    assert updated.payment_status == "succeeded"
    assert updated.payment_reference == "pi_test_123"


async def test_webhook_failed_updates_payment_status(client, stripe_configured):
    await _add_to_cart(client)
    cart = await _get_cart_order()

    payload = _intent_event("payment_intent.payment_failed", str(cart.id))
    resp = await _post_webhook(client, payload)

    assert resp.status_code == 200
    updated = await _get_cart_order()
    assert updated.payment_status == "failed"


async def test_webhook_invalid_signature_returns_400(client, stripe_configured):
    await _add_to_cart(client)
    cart = await _get_cart_order()

    payload = _intent_event("payment_intent.succeeded", str(cart.id))
    resp = await _post_webhook(client, payload, secret="whsec_wrong")

    assert resp.status_code == 400
    # The event must not have been applied.
    updated = await _get_cart_order()
    assert updated.payment_status == "pending"


async def test_webhook_ignores_unhandled_event_types(client, stripe_configured):
    payload = json.dumps(
        {
            "id": "evt_x",
            "object": "event",
            "type": "charge.refunded",
            "data": {"object": {}},
        }
    ).encode()

    resp = await _post_webhook(client, payload)

    assert resp.status_code == 200


async def test_webhook_unknown_order_is_acknowledged(client, stripe_configured):
    # Stripe retries non-2xx forever, so an unmatchable intent must still 200.
    payload = _intent_event(
        "payment_intent.succeeded", str(uuid.uuid4()), intent_id="pi_unknown"
    )

    resp = await _post_webhook(client, payload)

    assert resp.status_code == 200
