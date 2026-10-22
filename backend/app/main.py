"""HTTP entry point for the first CodeFlowAtlas API slice."""

import asyncio
import logging
from contextlib import asynccontextmanager



from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker
from app.auth.routes import router as auth_router
from app.projects.routes import router as projects_router

import os

from starlette.middleware.sessions import SessionMiddleware
from app.auth.oauth_routes import router as oauth_router
from app.auth.routes import COOKIE_SECURE

from app.db import create_engine


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI):
    engine = create_engine()
    application.state.db_engine = engine
    application.state.db_session_factory = async_sessionmaker(
        engine, expire_on_commit=False
    )
    try:
        yield
    finally:
        await engine.dispose()


app = FastAPI(
    title="CodeFlowAtlas API",
    description="Repository intelligence and engineering experiments",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ["OAUTH_STATE_SECRET"],
    session_cookie="cfa_oauth_flow",
    same_site="lax",
    https_only=COOKIE_SECURE,
    max_age=600,
)


@app.middleware("http")
async def protect_auth_posts(request, call_next):
    if (
        request.method in {"POST", "PUT", "PATCH", "DELETE"}
        and (request.url.path.startswith("/auth/") or request.url.path.startswith("/projects/"))
    ):
        expected = os.environ["APP_PUBLIC_URL"].rstrip("/")
        if request.headers.get("origin") != expected:
            return JSONResponse(
                status_code=403,
                content={"detail": "Invalid origin"},
            )

    return await call_next(request)

app.include_router(oauth_router)

app.include_router(auth_router)

app.include_router(projects_router)


@app.get("/health/live", tags=["health"])
async def liveness() -> dict[str, str]:
    """Report whether the API process can serve requests."""
    return {"status": "ok", "service": "codeflowatlas-api"}


async def _ping_database(engine: AsyncEngine) -> None:
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))


@app.get("/health/ready", tags=["health"])
async def readiness() -> JSONResponse:
    """Verify that PostgreSQL is reachable through the application engine."""
    try:
        await asyncio.wait_for(_ping_database(app.state.db_engine), timeout=3)
    except (OSError, TimeoutError, SQLAlchemyError):
        logger.warning("PostgreSQL readiness check failed")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unavailable", "service": "codeflowatlas-api", "dependency": "postgresql"},
        )

    return JSONResponse(content={"status": "ok", "service": "codeflowatlas-api", "dependency": "postgresql"})
