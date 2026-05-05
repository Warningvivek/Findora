"""
routers/search.py
─────────────────
GET /api/search?q=...&max_results=10&source_type=pdf

Returns:
  {
    "results": [...],
    "summary": "...",       ← AI-generated insight
    "query": "...",
    "total": N
  }
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.dependencies import get_current_user
from database.models import Memory, User, SearchHistory
from database.session import get_db
from services.embedding_service import search_index
from services.summarization_service import summarize_results

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("")
async def search_memories(
    q: str = Query(..., min_length=1, description="Search query"),
    max_results: int = Query(10, ge=1, le=50),
    source_type: Optional[str] = Query(None, description="Filter by type: pdf, note, image, txt"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # ── 1. Semantic search via FAISS ─────────────────────────────────────────
    try:
        hits = search_index(current_user.id, q, top_k=max_results * 2)
        # hits = [(memory_id, distance), ...]
    except Exception as e:
        logger.error("FAISS search error: %s", e)
        hits = []

    if not hits:
        # Save empty search history
        await _save_history(db, current_user.id, q, 0)
        return {"results": [], "summary": "", "query": q, "total": 0}

    # ── 2. Fetch memory rows from DB ─────────────────────────────────────────
    memory_ids = [mid for mid, _ in hits]
    dist_map   = {mid: dist for mid, dist in hits}

    stmt = select(Memory).where(
        Memory.id.in_(memory_ids),
        Memory.user_id == current_user.id,
    )
    rows = (await db.execute(stmt)).scalars().all()

    # Apply source_type filter if requested
    if source_type:
        rows = [r for r in rows if (r.source_type or "").lower() == source_type.lower()]

    if not rows:
        await _save_history(db, current_user.id, q, 0)
        return {"results": [], "summary": "", "query": q, "total": 0}

    # ── 3. Sort by FAISS distance (ascending = more similar) ─────────────────
    rows.sort(key=lambda r: dist_map.get(r.id, 9999))
    rows = rows[:max_results]

    # ── 4. Build result dicts ─────────────────────────────────────────────────
    results = []
    for mem in rows:
        dist  = dist_map.get(mem.id, 1.0)
        # Convert L2 distance → similarity score (0-1, higher = better)
        score = max(0.0, 1.0 - (dist / 2.0))
        results.append({
            "id":          mem.id,
            "title":       mem.title or "Untitled",
            "content":     mem.content or "",
            "source_type": mem.source_type or "note",
            "is_favorite": mem.is_favorite,
            "created_at":  mem.created_at.isoformat() if mem.created_at else None,
            "score":       round(score, 4),
        })

    # ── 5. Generate AI summary ────────────────────────────────────────────────
    summary = ""
    try:
        # Pass the top results as snippets for context
        snippets = [{"content": r["content"]} for r in results]
        summary = summarize_results(q, snippets)
        logger.info("Summary generated for query '%s': %s chars", q, len(summary))
    except Exception as e:
        logger.warning("Summary generation failed: %s", e)
        summary = ""

    # ── 6. Save search history ────────────────────────────────────────────────
    await _save_history(db, current_user.id, q, len(results))

    return {
        "results": results,
        "summary": summary,
        "query":   q,
        "total":   len(results),
    }


async def _save_history(db: AsyncSession, user_id: int, query: str, result_count: int):
    """Persist the search query to history (best-effort, non-blocking)."""
    try:
        entry = SearchHistory(
            user_id=user_id,
            query=query,
            result_count=result_count,
        )
        db.add(entry)
        await db.commit()
    except Exception as e:
        logger.warning("Failed to save search history: %s", e)
        await db.rollback()