from pydantic import BaseModel, Field


class CheckoutRequest(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    card_token: str
    notify_channel: str = "email"


class OrderResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    total_cents: int
    status: str