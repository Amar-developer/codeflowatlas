from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_session
from app.schemas import CheckoutRequest, OrderResponse
from app.services import inventory, notifications
from app.services.orders import OrderService
from app.services.payment import PaymentError, charge_card


router = APIRouter(prefix="/checkout", tags=["checkout"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def checkout(
    payload: CheckoutRequest,
    session: Annotated[Session, Depends(get_session)],
) -> OrderResponse:
    product = inventory.reserve(session, payload.product_id, payload.quantity)
    total_cents = product.price_cents * payload.quantity

    try:
        charge_card(payload.card_token, total_cents)
    except PaymentError as exc:
        session.rollback()
        raise HTTPException(status_code=402, detail=str(exc)) from exc

    order = OrderService(session).create(product.id, payload.quantity, total_cents)
    notifications.send(payload.notify_channel, order.id)
    return OrderResponse.model_validate(order, from_attributes=True)