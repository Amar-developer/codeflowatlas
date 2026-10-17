import logging
import os
import secrets
import smtplib
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import (
    SESSION_COOKIE,
    get_current_user,
    hash_token,
)
from app.auth.email import send_password_reset_email, send_verification_email
from app.auth.rate_limit import enforce_limit, refund_limit
from app.auth.schemas import (
    ForgotPasswordRequest,
    LoginRequest,
    ResendVerificationRequest,
    ResetPasswordRequest,
    SignupRequest,
    UserResponse,
    VerifyEmailRequest,
)
from app.auth.security import DUMMY_HASH, hash_password, verify_password
from app.db import get_db
from app.models.auth import (
    EmailVerificationToken,
    PasswordCredential,
    PasswordResetToken,
    User,
)
from app.models.auth import Session as UserSession


router = APIRouter(prefix="/auth", tags=["auth"])

SESSION_SECONDS = 7 * 24 * 60 * 60
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"


logger = logging.getLogger(__name__)
VERIFICATION_SECONDS = 24 * 60 * 60
RESEND_WAIT_SECONDS = 60

RESET_SECONDS = 30 * 60
RESET_REQUEST_WAIT_SECONDS = 60


def create_verification_token(db: AsyncSession, user_id) -> str:
    raw_token = secrets.token_urlsafe(32)

    db.add(
        EmailVerificationToken(
            user_id=user_id,
            token_hash=hash_token(raw_token),
            expires_at=datetime.now(timezone.utc)
            + timedelta(seconds=VERIFICATION_SECONDS),
        )
    )
    return raw_token


async def expire_unsent_token(
    db: AsyncSession,
    token_model: type[EmailVerificationToken] | type[PasswordResetToken],
    raw_token: str,
) -> None:
    await db.execute(
        update(token_model)
        .where(token_model.token_hash == hash_token(raw_token))
        .values(expires_at=datetime.now(timezone.utc))
    )
    await db.commit()


async def deliver_verification_email(address: str, token: str) -> bool:
    try:
        await run_in_threadpool(send_verification_email, address, token)
        return True
    except (OSError, smtplib.SMTPException):
        logger.exception("Could not send email verification message")
        return False


async def reject_invalid_login(email: str) -> None:
    await enforce_limit("login-failed", email, 8, 15 * 60)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password",
    )


@router.post("/login", response_model=UserResponse)
async def login(
    payload: LoginRequest,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    normalized_email = str(payload.email).strip().casefold()

    result = await db.execute(
        select(User, PasswordCredential)
        .join(PasswordCredential, PasswordCredential.user_id == User.id)
        .where(User.email_normalized == normalized_email)
    )
    row = result.one_or_none()

    if row is None:
        await run_in_threadpool(verify_password, payload.password, DUMMY_HASH)
        await reject_invalid_login(normalized_email)

    user, credential = row
    password_is_valid = await run_in_threadpool(
        verify_password, payload.password, credential.password_hash
    )

    if not password_is_valid or user.status != "active":
        await reject_invalid_login(normalized_email)

    if user.email_verified_at is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Verify your email before logging in",
        )

    token = secrets.token_urlsafe(32)
    token_hash = hash_token(token)

    db.add(
        UserSession(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=SESSION_SECONDS),
        )
    )
    await db.commit()

    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        max_age=SESSION_SECONDS,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        path="/",
    )
    return user



@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def signup(
    payload: SignupRequest,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    normalized_email = str(payload.email).strip().casefold()

    # Password hashing takes CPU time, so keep it off the event loop.
    stored_hash = await run_in_threadpool(hash_password, payload.password)

    user = User(
        email=str(payload.email),
        email_normalized=normalized_email,
        display_name=payload.display_name,
    )

    try:
        async with db.begin():
            db.add(user)
            await db.flush()  # Inserts the user and gives us its UUID.

            db.add(
                PasswordCredential(
                    user_id=user.id,
                    password_hash=stored_hash,
                )
            )
            raw_token = create_verification_token(db, user.id)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        ) from exc

    sent = await deliver_verification_email(str(payload.email), raw_token)

    if not sent:
        await expire_unsent_token(db, EmailVerificationToken, raw_token)
        response.status_code = status.HTTP_202_ACCEPTED

    return user


@router.get("/me", response_model=UserResponse)
async def me(user: Annotated[User, Depends(get_current_user)]) -> User:
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    cfa_session: Annotated[
        str | None, Cookie(alias=SESSION_COOKIE)
    ] = None,
) -> None:
    if cfa_session:
        await db.execute(
            update(UserSession)
            .where(
                UserSession.token_hash == hash_token(cfa_session),
                UserSession.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(timezone.utc))
        )
        await db.commit()

    response.delete_cookie(
        key=SESSION_COOKIE,
        path="/",
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
    )

@router.post("/verify-email", status_code=status.HTTP_204_NO_CONTENT)
async def verify_email(
    payload: VerifyEmailRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    now = datetime.now(timezone.utc)

    result = await db.execute(
        select(EmailVerificationToken)
        .where(EmailVerificationToken.token_hash == hash_token(payload.token))
        .with_for_update()
    )
    verification = result.scalar_one_or_none()

    if verification is None:
        raise HTTPException(
            status_code=400,
            detail="Verification link is invalid or expired",
        )

    user = await db.get(User, verification.user_id)
    if user is None:
        raise HTTPException(
            status_code=400,
            detail="Verification link is invalid or expired",
        )

    # Opening a link again after successful verification is harmless.
    if verification.consumed_at is not None:
        if user.email_verified_at is not None:
            return
        raise HTTPException(
            status_code=400,
            detail="Verification link is invalid or expired",
        )

    if verification.expires_at <= now:
        raise HTTPException(
            status_code=400,
            detail="Verification link is invalid or expired",
        )

    user.email_verified_at = now
    verification.consumed_at = now
    await db.commit()


@router.post("/resend-verification", status_code=status.HTTP_204_NO_CONTENT)
async def resend_verification(
    payload: ResendVerificationRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    normalized_email = str(payload.email).strip().casefold()
    await enforce_limit("verify-resend", normalized_email, 3, 60 * 60)

    user_result = await db.execute(
        select(User).where(User.email_normalized == normalized_email)
    )
    user = user_result.scalar_one_or_none()

    # Same response for unknown, verified, and pending addresses.
    if user is None or user.email_verified_at is not None:
        return

    latest_result = await db.execute(
        select(EmailVerificationToken)
        .where(EmailVerificationToken.user_id == user.id)
        .order_by(EmailVerificationToken.created_at.desc())
        .limit(1)
    )
    latest = latest_result.scalar_one_or_none()

    if latest is not None and latest.expires_at > datetime.now(timezone.utc):
        elapsed = datetime.now(timezone.utc) - latest.created_at
        if elapsed.total_seconds() < RESEND_WAIT_SECONDS:
            return

    raw_token = create_verification_token(db, user.id)
    await db.commit()

    sent = await deliver_verification_email(user.email, raw_token)
    if not sent:
        await expire_unsent_token(db, EmailVerificationToken, raw_token)
        await refund_limit("verify-resend", normalized_email)


@router.post("/forgot-password", status_code=status.HTTP_204_NO_CONTENT)
async def forgot_password(
    payload: ForgotPasswordRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    normalized_email = str(payload.email).strip().casefold()
    await enforce_limit("password-email", normalized_email, 3, 60 * 60)

    user = await db.scalar(
        select(User).where(User.email_normalized == normalized_email)
    )

    # OAuth accounts already have a verified email. Unverified accounts
    # should finish the separate email-verification flow first.
    if (
        user is None
        or user.status != "active"
        or user.email_verified_at is None
    ):
        return

    latest = await db.scalar(
        select(PasswordResetToken)
        .where(PasswordResetToken.user_id == user.id)
        .order_by(PasswordResetToken.created_at.desc())
        .limit(1)
    )

    if latest is not None and latest.expires_at > datetime.now(timezone.utc):
        elapsed = datetime.now(timezone.utc) - latest.created_at
        if elapsed.total_seconds() < RESET_REQUEST_WAIT_SECONDS:
            return

    raw_token = secrets.token_urlsafe(32)
    db.add(
        PasswordResetToken(
            user_id=user.id,
            token_hash=hash_token(raw_token),
            expires_at=datetime.now(timezone.utc)
            + timedelta(seconds=RESET_SECONDS),
        )
    )
    await db.commit()

    try:
        await run_in_threadpool(
            send_password_reset_email, user.email, raw_token
        )
    except (OSError, smtplib.SMTPException):
        logger.exception("Could not send password reset email")
        await expire_unsent_token(db, PasswordResetToken, raw_token)
        await refund_limit("password-email", normalized_email)


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(
    payload: ResetPasswordRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    invalid_link = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Reset link is invalid or expired",
    )

    async with db.begin():
        reset = await db.scalar(
            select(PasswordResetToken).where(
                PasswordResetToken.token_hash == hash_token(payload.token)
            )
        )
        if reset is None:
            raise invalid_link

        # Serialize password resets for this user, including when two
        # different valid links are submitted at the same time.
        user = await db.scalar(
            select(User)
            .where(User.id == reset.user_id)
            .with_for_update()
        )
        if user is None:
            raise invalid_link

        # Reload after acquiring the user lock: another reset may have
        # consumed this link while we waited.
        await db.refresh(reset)
        now = datetime.now(timezone.utc)

        if (
            reset.consumed_at is not None
            or reset.expires_at <= now
            or user.status != "active"
            or user.email_verified_at is None
        ):
            raise invalid_link

        new_hash = await run_in_threadpool(
            hash_password, payload.new_password
        )

        credential = await db.get(PasswordCredential, user.id)
        if credential is None:
            db.add(
                PasswordCredential(
                    user_id=user.id,
                    password_hash=new_hash,
                )
            )
        else:
            credential.password_hash = new_hash
            credential.changed_at = now

        # Using one link invalidates all other reset links for this user.
        await db.execute(
            update(PasswordResetToken)
            .where(
                PasswordResetToken.user_id == user.id,
                PasswordResetToken.consumed_at.is_(None),
            )
            .values(consumed_at=now)
        )

        # Require login again on all devices.
        await db.execute(
            update(UserSession)
            .where(
                UserSession.user_id == user.id,
                UserSession.revoked_at.is_(None),
            )
            .values(revoked_at=now)
        )
