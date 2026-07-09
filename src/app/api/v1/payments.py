from fastapi import APIRouter, Depends, HTTPException, Request

import stripe

from app.api.deps import get_payment_service
from app.core.security import CurrentUser
from app.domain.schemas.payment import CreatePaymentIntentResponseDTO
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/create-intent", response_model=CreatePaymentIntentResponseDTO)
async def create_payment_intent(
    current_user: CurrentUser,
    service: PaymentService = Depends(get_payment_service),
):
    """Create a PaymentIntent for the buyer's cart and return its client secret."""
    intent = await service.create_intent(current_user.id)
    return CreatePaymentIntentResponseDTO(
        client_secret=intent.client_secret,
        payment_intent_id=intent.id,
    )


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    service: PaymentService = Depends(get_payment_service),
):
    """Receive Stripe events. No JWT — the signature header is the auth."""
    # Verification needs the exact raw bytes Stripe signed, so the body is
    # read manually instead of letting FastAPI parse it.
    payload = await request.body()
    signature = request.headers.get("stripe-signature", "")
    try:
        await service.handle_webhook(payload, signature)
    except (ValueError, stripe.SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")
    return {"received": True}
