from sqlalchemy.orm import Session

from app.models import Order


class OrderService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, product_id: int, quantity: int, total_cents: int) -> Order:
        order = Order(
            product_id=product_id,
            quantity=quantity,
            total_cents=total_cents,
            status="paid",
        )
        self.session.add(order)
        self.session.commit()
        self.session.refresh(order)
        return order

    def get(self, order_id: int) -> Order | None:
        return self.session.get(Order, order_id)