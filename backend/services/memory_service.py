"""
services/memory_service.py
───────────────────────────
Business logic for CRUD operations on Memory records.
Coordinates between DB, FAISS index, and file storage.
"""

import logging
from typing import List, Optional

from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Memory, SearchHistory
from services import embedding_service, file_service

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Create
# ─────────────────────────────────────────────────────────────────────────────

async def create_note(
    db: AsyncSession,
    user_id: int,
    title: str,
    content: str,
    tags: List[str] = None,
) -> Memory:
    """Create a text note and index it."""
    memory = Memory(
        user_id=user_id,
        title=title,
        content=content,
        source_type="note",
        tags=tags or [],
    )
    db.add(memory)
    await db.flush()   # get the PK without committing

    # Add to FAISS
    index_text = f"{title} {content}"
    row = embedding_service.add_to_index(user_id, memory.id, index_text)
    memory.faiss_index = row

    await db.flush()
    logger.info("Created note id=%d for user %d", memory.id, user_id)
    return memory


async def create_file_memory(
    db: AsyncSession,
    user_id: int,
    title: str,
    file_path: str,
    file_name: str,
    source_type: str,
    extracted_text: str,
    tags: List[str] = None,
) -> Memory:
    """Create a Memory backed by an uploaded file."""
    memory = Memory(
        user_id=user_id,
        title=title,
        content=extracted_text,
        source_type=source_type,
        file_path=file_path,
        file_name=file_name,
        tags=tags or [],
    )
    db.add(memory)
    await db.flush()

    index_text = f"{title} {extracted_text}"
    row = embedding_service.add_to_index(user_id, memory.id, index_text)
    memory.faiss_index = row

    await db.flush()
    logger.info("Created %s memory id=%d for user %d", source_type, memory.id, user_id)
    return memory


# ─────────────────────────────────────────────────────────────────────────────
# Read
# ─────────────────────────────────────────────────────────────────────────────

async def get_memory(db: AsyncSession, user_id: int, memory_id: int) -> Optional[Memory]:
    result = await db.execute(
        select(Memory).where(Memory.id == memory_id, Memory.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def list_memories(
    db: AsyncSession,
    user_id: int,
    source_type: Optional[str] = None,
    tag: Optional[str] = None,
    favorites_only: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> List[Memory]:
    q = select(Memory).where(Memory.user_id == user_id)

    if source_type:
        q = q.where(Memory.source_type == source_type)
    if favorites_only:
        q = q.where(Memory.is_favorite == True)
    if tag:
        # SQLite JSON contains – works via JSON function
        q = q.where(Memory.tags.contains([tag]))

    q = q.order_by(desc(Memory.created_at)).limit(limit).offset(offset)
    result = await db.execute(q)
    return result.scalars().all()


async def count_memories(db: AsyncSession, user_id: int) -> int:
    result = await db.execute(
        select(func.count()).where(Memory.user_id == user_id)
    )
    return result.scalar_one()


# ─────────────────────────────────────────────────────────────────────────────
# Update
# ─────────────────────────────────────────────────────────────────────────────

async def toggle_favorite(db: AsyncSession, user_id: int, memory_id: int) -> Optional[Memory]:
    memory = await get_memory(db, user_id, memory_id)
    if not memory:
        return None
    memory.is_favorite = not memory.is_favorite
    await db.flush()
    return memory


async def update_tags(db: AsyncSession, user_id: int, memory_id: int, tags: List[str]) -> Optional[Memory]:
    memory = await get_memory(db, user_id, memory_id)
    if not memory:
        return None
    memory.tags = tags
    await db.flush()
    return memory


# ─────────────────────────────────────────────────────────────────────────────
# Delete
# ─────────────────────────────────────────────────────────────────────────────

async def delete_memory(db: AsyncSession, user_id: int, memory_id: int) -> bool:
    memory = await get_memory(db, user_id, memory_id)
    if not memory:
        return False

    # Remove from FAISS
    embedding_service.remove_from_index(user_id, memory_id)

    # Remove file from disk
    if memory.file_path:
        file_service.delete_file(memory.file_path)

    await db.delete(memory)
    await db.flush()
    logger.info("Deleted memory id=%d for user %d", memory_id, user_id)
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Search History
# ─────────────────────────────────────────────────────────────────────────────

async def log_search(db: AsyncSession, user_id: int, query: str, result_count: int) -> None:
    history = SearchHistory(user_id=user_id, query=query, result_count=result_count)
    db.add(history)
    await db.flush()


async def get_recent_searches(db: AsyncSession, user_id: int, limit: int = 10) -> List[SearchHistory]:
    result = await db.execute(
        select(SearchHistory)
        .where(SearchHistory.user_id == user_id)
        .order_by(desc(SearchHistory.searched_at))
        .limit(limit)
    )
    return result.scalars().all()
