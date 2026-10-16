from fastapi import FastAPI

from app.routers import checkout, orders

app = FastAPI(title="Fixture Shop")
app.include_router(checkout.router, prefix="/api")
app.include_router(orders.router, prefix="/api")