"""
routers/memories.py
────────────────────
Endpoints:
  POST   /api/memories/notes          – create text note
  POST   /api/memories/upload         – upload PDF / TXT / image
  GET    /api/memories                – list user's memories (with filters)
  GET    /api/memories/{id}           – single memory detail
  DELETE /api/memories/{id}           – delete memory
  PATCH  /api/memories/{id}/favorite  – toggle favorite
  PATCH  /api/memories/{id}/tags      – update tags
  GET    /api/memories/stats          – dashboard statistics
"""

from typing import List, Optional
import io

from fastapi import (
    APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from database.session import get_db
from database.models import User, Memory, SearchHistory
from core.dependencies import get_current_user
from models.schemas import (
    NoteCreate, MemoryOut, MemoryList, TagUpdate, StatsOut, SearchHistoryOut
)
from services import memory_service, file_service

router = APIRouter(prefix="/api/memories", tags=["Memories"])


# ── Notes ─────────────────────────────────────────────────────────────────────

@router.post("/notes", response_model=MemoryOut, status_code=201)
async def create_note(
    payload: NoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a plain text note."""
    note = await memory_service.create_note(
        db, current_user.id, payload.title, payload.content, payload.tags
    )
    return note


# ── File Upload ───────────────────────────────────────────────────────────────

@router.post("/upload", response_model=MemoryOut, status_code=201)
async def upload_file(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    tags: Optional[str] = Form(""),       # comma-separated
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a PDF, TXT, or image file and index its extracted text."""
    raw = await file.read()

    # Validate
    ok, err = file_service.validate_file(file.filename, len(raw))
    if not ok:
        raise HTTPException(status_code=400, detail=err)

    source_type = file_service.detect_source_type(file.filename)
    if source_type == "unknown":
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Save to disk
    path = file_service.save_upload(raw, file.filename, current_user.id)

    # Extract text
    extracted = file_service.extract_text(str(path), source_type)

    # Parse tags
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []

    memory = await memory_service.create_file_memory(
        db=db,
        user_id=current_user.id,
        title=title or file.filename,
        file_path=str(path),
        file_name=file.filename,
        source_type=source_type,
        extracted_text=extracted,
        tags=tag_list,
    )
    return memory


# ── List & Retrieve ───────────────────────────────────────────────────────────

@router.get("", response_model=MemoryList)
async def list_memories(
    source_type: Optional[str] = Query(None, description="Filter by type: note|pdf|txt|image"),
    tag: Optional[str] = Query(None),
    favorites: bool = Query(False),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = await memory_service.list_memories(
        db, current_user.id, source_type, tag, favorites, limit, offset
    )
    total = await memory_service.count_memories(db, current_user.id)
    return MemoryList(items=items, total=total)


@router.get("/stats", response_model=StatsOut)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Dashboard statistics for the current user."""
    # Count by type
    result = await db.execute(
        select(Memory.source_type, func.count())
        .where(Memory.user_id == current_user.id)
        .group_by(Memory.source_type)
    )
    by_type = {row[0]: row[1] for row in result.all()}

    # Favorites count
    fav_result = await db.execute(
        select(func.count())
        .where(Memory.user_id == current_user.id, Memory.is_favorite == True)
    )
    favorites = fav_result.scalar_one()

    total = sum(by_type.values())

    searches = await memory_service.get_recent_searches(db, current_user.id, limit=5)

    return StatsOut(
        total_memories=total,
        by_type=by_type,
        favorites=favorites,
        recent_searches=[SearchHistoryOut.model_validate(s) for s in searches],
    )


@router.get("/{memory_id}", response_model=MemoryOut)
async def get_memory(
    memory_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    memory = await memory_service.get_memory(db, current_user.id, memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory


# ── Update ────────────────────────────────────────────────────────────────────

@router.patch("/{memory_id}/favorite", response_model=MemoryOut)
async def toggle_favorite(
    memory_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    memory = await memory_service.toggle_favorite(db, current_user.id, memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory


@router.patch("/{memory_id}/tags", response_model=MemoryOut)
async def update_tags(
    memory_id: int,
    payload: TagUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    memory = await memory_service.update_tags(db, current_user.id, memory_id, payload.tags)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory


# ── Delete ────────────────────────────────────────────────────────────────────

@router.delete("/{memory_id}", status_code=204)
async def delete_memory(
    memory_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = await memory_service.delete_memory(db, current_user.id, memory_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory not found")
