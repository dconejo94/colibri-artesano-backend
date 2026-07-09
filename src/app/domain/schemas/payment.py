from pydantic import BaseModel, Field


class CreatePaymentIntentResponseDTO(BaseModel):
    # camelCase aliases: the mobile client (types/orders.ts) already expects
    # {clientSecret, paymentIntentId}, unlike the rest of the snake_case API.
    client_secret: str = Field(serialization_alias="clientSecret")
    payment_intent_id: str = Field(serialization_alias="paymentIntentId")
