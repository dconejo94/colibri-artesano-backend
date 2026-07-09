from uuid import UUID

import stripe

from app.config import settings
from app.core.exceptions import ConflictException, ServiceUnavailableException
from app.domain.models.main_order import MainOrder
from app.repositories.order_repository import OrderRepository


class PaymentService:
    def __init__(self, order_repository: OrderRepository):
        self.order_repo = order_repository

    async def create_intent(self, buyer_id: UUID) -> stripe.PaymentIntent:
        """Create a Stripe PaymentIntent for the buyer's current cart."""
        if not settings.STRIPE_SECRET_KEY:
            raise ServiceUnavailableException(
                "Los pagos no están disponibles en este momento."
            )

        cart = await self.order_repo.get_cart_by_buyer(buyer_id)
        has_items = cart is not None and any(
            store_order.items for store_order in cart.store_orders
        )
        if not has_items:
            raise ConflictException("El carrito está vacío")

        # Stripe expects integer minor units (10.50 USD -> 1050). total_amount
        # is a Decimal, so this conversion is exact — no float math.
        amount = int(cart.total_amount * 100)

        # The cart row becomes the placed order under the same id, so tagging
        # the intent with it lets the webhook find the order later. Including
        # the amount in the idempotency key makes a retried request reuse the
        # same intent, while a cart changed since then gets a fresh one.
        intent = await stripe.PaymentIntent.create_async(
            api_key=settings.STRIPE_SECRET_KEY,
            amount=amount,
            currency=settings.STRIPE_CURRENCY,
            metadata={"order_id": str(cart.id)},
            automatic_payment_methods={"enabled": True},
            idempotency_key=f"cart-{cart.id}-{amount}",
        )

        cart.payment_reference = intent.id
        cart.payment_method = "card"
        cart.payment_status = "pending"
        await self.order_repo.flush()

        return intent

    async def handle_webhook(self, payload: bytes, signature: str) -> None:
        """Verify and apply a Stripe webhook event.

        Raises ValueError / stripe.SignatureVerificationError on bad payloads,
        which the route maps to a 400 so Stripe knows the delivery failed.
        """
        event = stripe.Webhook.construct_event(
            payload, signature, settings.STRIPE_WEBHOOK_SECRET
        )

        if event["type"] == "payment_intent.succeeded":
            await self._update_payment_status(event, "succeeded")
        elif event["type"] == "payment_intent.payment_failed":
            await self._update_payment_status(event, "failed")
        # Other event types are acknowledged and ignored: a non-2xx would only
        # put deliveries we never handle into Stripe's retry loop.

    async def _update_payment_status(self, event: stripe.Event, status: str) -> None:
        intent = event["data"]["object"]
        order = await self._find_order(intent)
        if order is None:
            # Unknown order (e.g. an intent created outside this app): ack and
            # skip rather than making Stripe retry forever. Idempotent by
            # design — Stripe may deliver the same event more than once.
            return
        order.payment_status = status
        if order.payment_reference is None:
            order.payment_reference = intent["id"]
        await self.order_repo.flush()

    async def _find_order(self, intent) -> MainOrder | None:
        # StripeObject supports [] access but not dict.get().
        try:
            order_id = intent["metadata"]["order_id"]
        except (KeyError, TypeError):
            order_id = None
        if order_id:
            try:
                order = await self.order_repo.get_main_order_by_id(UUID(order_id))
            except ValueError:
                order = None
            if order is not None:
                return order
        # Fallback for intents missing our metadata but known by reference.
        return await self.order_repo.get_main_order_by_payment_reference(intent["id"])
