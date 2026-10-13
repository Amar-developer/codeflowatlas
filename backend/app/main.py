"""HTTP entry point for the first CodeFlowAtlas API slice."""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

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
