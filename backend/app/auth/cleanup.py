import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete

from app.db import create_engine
from app.models.auth import (
    EmailVerificationToken,
    PasswordResetToken,
    Session,
)


async def main() -> None:
    engine = create_engine()
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)

    try:
        async with engine.begin() as connection:
            await connection.execute(
                delete(EmailVerificationToken).where(
                    EmailVerificationToken.expires_at < cutoff
                )
            )
            await connection.execute(
                delete(PasswordResetToken).where(
                    PasswordResetToken.expires_at < cutoff
                )
            )
            await connection.execute(
                delete(Session).where(Session.expires_at < cutoff)
            )
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())