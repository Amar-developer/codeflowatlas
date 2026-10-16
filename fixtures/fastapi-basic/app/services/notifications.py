def send_email(order_id: int) -> None:
    print(f"Email sent for order {order_id}")


def send_sms(order_id: int) -> None:
    print(f"SMS sent for order {order_id}")


def send(channel: str, order_id: int) -> None:
    # Dynamic dispatch: static analysis cannot know which function runs.
    handler = globals()[f"send_{channel}"]
    handler(order_id)