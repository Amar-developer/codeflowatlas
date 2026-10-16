import os

import httpx


PAYMENT_URL = os.environ.get("PAYMENT_URL", "http://payments.local/charge")


class PaymentError(Exception):
    pass


def charge_card(card_token: str, amount_cents: int) -> str:
    response = httpx.post(
        PAYMENT_URL,
        json={"token": card_token, "amount": amount_cents},
        timeout=5.0,
    )
    if response.status_code != 200:
        raise PaymentError("Payment was declined")
    return response.json()["charge_id"]