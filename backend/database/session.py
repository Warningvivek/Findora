"""
database/session.py
───────────────────
Async SQLAlchemy engine + session factory.
Call `init_db()` once at application startup to create all tables.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from database.models import Base
from core.config import settings
from database import models
# ── Engine ────────────────────────────────────────────────────────────────────
# StaticPool is used for SQLite so that in-memory tests share one connection.
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,                   # Set True for SQL debug logging
    connect_args={"check_same_thread": False},   # SQLite only
)

# ── Session factory ───────────────────────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def init_db() -> None:
    """Create all tables on startup (idempotent)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    """FastAPI dependency that yields an async DB session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
