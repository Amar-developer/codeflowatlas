import hashlib
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.auth import Session as UserSession
from app.models.auth import User


SESSION_COOKIE = "cfa_session"


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


async def get_current_session(
    db: Annotated[AsyncSession, Depends(get_db)],
    cfa_session: Annotated[str | None, Cookie()] = None,
) -> tuple[UserSession, User]:
    """Resolve the session cookie to an active, unexpired, unrevoked session."""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )
    if not cfa_session:
        raise unauthorized

    result = await db.execute(
        select(UserSession, User)
        .join(User, User.id == UserSession.user_id)
        .where(
            UserSession.token_hash == hash_token(cfa_session),
            UserSession.revoked_at.is_(None),
            UserSession.expires_at > func.now(),
            User.status == "active",
        )
    )
    row = result.one_or_none()
    if row is None:
        raise unauthorized
    return row.tuple()


async def get_current_user(
    current: Annotated[tuple[UserSession, User], Depends(get_current_session)],
) -> User:
    return current[1]