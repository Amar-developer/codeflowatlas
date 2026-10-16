import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Annotated, Literal

import httpx
from authlib.integrations.base_client import OAuthError
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import SESSION_COOKIE, get_current_session, hash_token
from app.auth.oauth_client import oauth
from app.auth.routes import COOKIE_SECURE, SESSION_SECONDS
from app.db import get_db
from app.models.auth import OAuthIdentity, User
from app.models.auth import Session as UserSession


router = APIRouter(prefix="/auth/oauth", tags=["auth"])
Provider = Literal["google", "github"]


def frontend_redirect(error: str | None = None) -> RedirectResponse:
    frontend_url = os.environ["APP_PUBLIC_URL"].rstrip("/")
    destination = (
        f"{frontend_url}/login?error={error}"
        if error
        else f"{frontend_url}/dashboard"
    )
    return RedirectResponse(destination, status_code=303)


def link_redirect(
    provider: Provider,
    error: str | None = None,
) -> RedirectResponse:
    frontend_url = os.environ["APP_PUBLIC_URL"].rstrip("/")
    query = (
        f"link_error={error}"
        if error
        else f"linked={provider}"
    )
    return RedirectResponse(
        f"{frontend_url}/dashboard?{query}",
        status_code=303,
    )


def callback_url(provider: Provider) -> str:
    return (
        os.environ["OAUTH_PUBLIC_BASE_URL"].rstrip("/")
        + f"/auth/oauth/{provider}/callback"
    )


@router.get("/{provider}/start")
async def oauth_start(provider: Provider, request: Request):
    # Ordinary sign-in must not reuse an abandoned linking attempt.
    request.session.pop("link_provider", None)
    request.session.pop("link_user_id", None)

    client = oauth.create_client(provider)
    return await client.authorize_redirect(
        request,
        callback_url(provider),
    )


@router.get("/{provider}/link/start")
async def oauth_link_start(
    provider: Provider,
    request: Request,
    current: Annotated[
        tuple[UserSession, User],
        Depends(get_current_session),
    ],
):
    _, user = current

    request.session["link_provider"] = provider
    request.session["link_user_id"] = str(user.id)

    client = oauth.create_client(provider)
    return await client.authorize_redirect(
        request,
        callback_url(provider),
    )


@router.get("/{provider}/callback")
async def oauth_callback(
    provider: Provider,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    link_provider = request.session.pop("link_provider", None)
    link_user_id = request.session.pop("link_user_id", None)

    if link_provider is not None and (
        link_provider != provider or not isinstance(link_user_id, str)
    ):
        request.session.clear()
        return link_redirect(provider, "link_failed")

    linking = link_provider == provider

    def failed(code: str) -> RedirectResponse:
        request.session.clear()
        if linking:
            return link_redirect(provider, code)
        return frontend_redirect(code)

    if request.query_params.get("error"):
        return failed("oauth_cancelled")

    client = oauth.create_client(provider)

    try:
        token = await client.authorize_access_token(request)

        if provider == "google":
            profile = token["userinfo"]

            if profile.get("email_verified") is not True:
                return failed("email_unverified")

            subject = str(profile["sub"])
            email = str(profile["email"])
            display_name = profile.get("name")

        else:
            user_response = await client.get("user", token=token)
            user_response.raise_for_status()
            profile = user_response.json()

            emails_response = await client.get(
                "user/emails",
                token=token,
            )
            emails_response.raise_for_status()
            emails = emails_response.json()

            verified_primary = next(
                (
                    item
                    for item in emails
                    if item.get("primary") is True
                    and item.get("verified") is True
                ),
                None,
            )

            if verified_primary is None:
                return failed("email_unverified")

            subject = str(profile["id"])
            email = str(verified_primary["email"])
            display_name = profile.get("name") or profile.get("login")

    except (OAuthError, httpx.HTTPError, KeyError, TypeError, ValueError):
        return failed("oauth_failed")

    identity = await db.scalar(
        select(OAuthIdentity).where(
            OAuthIdentity.provider == provider,
            OAuthIdentity.provider_subject == subject,
        )
    )

    # This branch connects a provider to the user who is already logged in.
    if linking:
        try:
            _, current_user = await get_current_session(
                db,
                request.cookies.get(SESSION_COOKIE),
            )
        except HTTPException:
            return failed("login_required")

        if str(current_user.id) != link_user_id:
            return failed("link_failed")

        if identity is not None and identity.user_id != current_user.id:
            return failed("provider_already_linked")

        existing_for_user = await db.scalar(
            select(OAuthIdentity).where(
                OAuthIdentity.user_id == current_user.id,
                OAuthIdentity.provider == provider,
            )
        )

        if (
            existing_for_user is not None
            and existing_for_user.provider_subject != subject
        ):
            return failed("provider_already_connected")

        if identity is None:
            db.add(
                OAuthIdentity(
                    user_id=current_user.id,
                    provider=provider,
                    provider_subject=subject,
                )
            )
            try:
                await db.commit()
            except IntegrityError:
                await db.rollback()
                return failed("link_failed")

        request.session.clear()
        return link_redirect(provider)

    # This branch is ordinary sign-in or first-time signup.
    if identity is not None:
        user = await db.get(User, identity.user_id)

        if user is None or user.status != "active":
            return failed("oauth_failed")
    else:
        normalized_email = email.strip().casefold()
        existing_user = await db.scalar(
            select(User).where(
                User.email_normalized == normalized_email
            )
        )

        if existing_user is not None:
            return failed("account_exists")

        user = User(
            email=email,
            email_normalized=normalized_email,
            display_name=str(display_name)[:100] if display_name else None,
            email_verified_at=datetime.now(timezone.utc),
        )
        db.add(user)
        await db.flush()

        db.add(
            OAuthIdentity(
                user_id=user.id,
                provider=provider,
                provider_subject=subject,
            )
        )

    raw_session = secrets.token_urlsafe(32)
    db.add(
        UserSession(
            user_id=user.id,
            token_hash=hash_token(raw_session),
            expires_at=(
                datetime.now(timezone.utc)
                + timedelta(seconds=SESSION_SECONDS)
            ),
        )
    )

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        return failed("oauth_failed")

    request.session.clear()

    response = frontend_redirect()
    response.set_cookie(
        key=SESSION_COOKIE,
        value=raw_session,
        max_age=SESSION_SECONDS,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        path="/",
    )
    return response