import os
import smtplib
from email.message import EmailMessage
from urllib.parse import urlencode


def send_verification_email(address: str, token: str) -> None:
    app_url = os.environ["APP_PUBLIC_URL"].rstrip("/")
    link = f"{app_url}/verify-email?{urlencode({'token': token})}"

    message = EmailMessage()
    message["Subject"] = "Verify your CodeFlowAtlas email"
    message["From"] = os.environ["EMAIL_FROM"]
    message["To"] = address
    message.set_content(
        "Welcome to CodeFlowAtlas.\n\n"
        f"Verify your email by opening this link:\n{link}\n\n"
        "This link expires in 24 hours. If you did not create an account, "
        "you can ignore this message.\n"
    )

    host = os.environ["SMTP_HOST"]
    port = int(os.environ.get("SMTP_PORT", "1025"))

    with smtplib.SMTP(host, port, timeout=10) as smtp:
        if os.environ.get("SMTP_STARTTLS", "false").lower() == "true":
            smtp.starttls()

        username = os.environ.get("SMTP_USER")
        if username:
            smtp.login(username, os.environ["SMTP_PASSWORD"])

        smtp.send_message(message)
        
        
        
def send_password_reset_email(address: str, token: str) -> None:
    app_url = os.environ["APP_PUBLIC_URL"].rstrip("/")
    link = f"{app_url}/reset-password?{urlencode({'token': token})}"

    message = EmailMessage()
    message["Subject"] = "Reset your CodeFlowAtlas password"
    message["From"] = os.environ["EMAIL_FROM"]
    message["To"] = address
    message.set_content(
        "Open this link to set a new CodeFlowAtlas password:\n\n"
        f"{link}\n\n"
        "This link expires in 30 minutes. If you did not request it, "
        "you can ignore this email.\n"
    )

    host = os.environ["SMTP_HOST"]
    port = int(os.environ.get("SMTP_PORT", "1025"))

    with smtplib.SMTP(host, port, timeout=10) as smtp:
        if os.environ.get("SMTP_STARTTLS", "false").lower() == "true":
            smtp.starttls()

        username = os.environ.get("SMTP_USER")
        if username:
            smtp.login(username, os.environ["SMTP_PASSWORD"])

        smtp.send_message(message)        