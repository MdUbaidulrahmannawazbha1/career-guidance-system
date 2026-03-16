"""
Async SQLAlchemy database engine, session factory, and base model.

Usage
-----
Depend on ``get_db`` in FastAPI route functions::

    from app.database import get_db
    from sqlalchemy.ext.asyncio import AsyncSession
    from fastapi import Depends

    @router.get("/example")
    async def example(db: AsyncSession = Depends(get_db)):
        ...
"""

from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,         # verify connections before use
    pool_recycle=1800,          # recycle connections every 30 minutes
    future=True,
)

# ---------------------------------------------------------------------------
# Session factory
# ---------------------------------------------------------------------------
AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# ---------------------------------------------------------------------------
# Declarative base
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.

    Every model that inherits from ``Base`` will be picked up by Alembic
    for auto-generating migrations.
    """


# ---------------------------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------------------------


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Yield an async database session and guarantee it is closed afterwards.

    Transaction management (commit / rollback) is the responsibility of the
    caller (service layer or route handler) so that business-logic boundaries
    determine when data is persisted.

    This function is designed to be used as a FastAPI dependency::

        db: AsyncSession = Depends(get_db)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ---------------------------------------------------------------------------
# Startup / shutdown helpers (called from app.main lifespan)
# ---------------------------------------------------------------------------


async def init_db() -> None:
    """
    Create all tables defined in ORM models.

    In production, Alembic migrations should be used instead.  This helper
    is primarily useful during development and testing.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Dispose the connection pool gracefully on application shutdown."""
    await engine.dispose()


# ---------------------------------------------------------------------------
# Health-check helper
# ---------------------------------------------------------------------------


async def check_db_connection() -> bool:
    """
    Return *True* if the database is reachable, *False* otherwise.

    Useful for liveness / readiness probe endpoints.
    """
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
