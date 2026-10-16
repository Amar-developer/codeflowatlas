from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Product


class OutOfStockError(Exception):
    pass


def reserve(session: Session, product_id: int, quantity: int) -> Product:
    product = session.scalars(select(Product).where(Product.id == product_id)).one()
    if product.stock < quantity:
        raise OutOfStockError(f"Only {product.stock} left")
    product.stock -= quantity
    return product