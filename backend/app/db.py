
import os
from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for persistent product models."""


def database_url() -> URL:
    """Build a URL without manually escaping credentials."""
    return URL.create(
        "postgresql+psycopg_async",
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=int(os.environ.get("DB_PORT", "5432")),
        database=os.environ["DB_NAME"],
    )


def create_engine() -> AsyncEngine:
    return create_async_engine(database_url(), pool_pre_ping=True)


async def get_db(request: Request) -> AsyncIterator[AsyncSession]:
    """Provide one session per request; callers own their transactions."""
    session_factory: async_sessionmaker[AsyncSession] = request.app.state.db_session_factory
    async with session_factory() as session:
        yield session
