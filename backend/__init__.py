"""
init_db.py  —  Run this ONCE from your project root to create all tables:

    python init_db.py

This is safe to run multiple times — it uses CREATE TABLE IF NOT EXISTS.
"""

import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init():
    # Import here so settings/env are loaded first
    from database.session import engine
    from database.models import Base   # imports all ORM models

    logger.info("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ All tables created successfully!")
    logger.info("Tables: %s", list(Base.metadata.tables.keys()))


if __name__ == "__main__":
    asyncio.run(init())