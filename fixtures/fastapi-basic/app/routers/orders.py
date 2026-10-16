from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_session
from app.schemas import OrderResponse
from app.services.orders import OrderService


router = APIRouter(prefix="/orders", tags=["orders"])


def get_order_service(session: Annotated[Session, Depends(get_session)]) -> OrderService:
    return OrderService(session)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    service: Annotated[OrderService, Depends(get_order_service)],
) -> OrderResponse:
    order = service.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return OrderResponse.model_validate(order, from_attributes=True)