"""HTTP entry point for the first CodeFlowAtlas API slice."""

import asyncio
import logging
import os

import asyncpg
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse


logger = logging.getLogger(__name__)

app = FastAPI(
    title="CodeFlowAtlas API",
    description="Repository intelligence and engineering experiments",
    version="0.1.0",
)


@app.get("/health/live", tags=["health"])
async def liveness() -> dict[str, str]:
    """Report whether the API process can serve requests."""
    return {"status": "ok", "service": "codeflowatlas-api"}


@app.get("/health/ready", tags=["health"])
async def readiness() -> JSONResponse:
    """Verify that PostgreSQL is reachable and accepts a simple query."""
    try:
        connection = await asyncpg.connect(
            host=os.environ["DB_HOST"],
            port=int(os.environ.get("DB_PORT", "5432")),
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            database=os.environ["DB_NAME"],
            timeout=3,
        )
        try:
            await connection.execute("SELECT 1")
        finally:
            await connection.close()
    except (KeyError, ValueError, OSError, TimeoutError, asyncio.TimeoutError, asyncpg.PostgresError, asyncpg.InterfaceError):
        logger.warning("PostgreSQL readiness check failed")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unavailable", "service": "codeflowatlas-api", "dependency": "postgresql"},
        )

    return JSONResponse(content={"status": "ok", "service": "codeflowatlas-api", "dependency": "postgresql"})
