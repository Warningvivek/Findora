"""
models/schemas.py
──────────────────
Pydantic v2 request/response schemas for all API endpoints.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


# ─────────────────────────────────────────────────────────────────────────────
# Auth
# ─────────────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ─────────────────────────────────────────────────────────────────────────────
# Memory
# ─────────────────────────────────────────────────────────────────────────────

class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=512)
    content: str = Field(..., min_length=1)
    tags: List[str] = Field(default_factory=list)


class MemoryOut(BaseModel):
    id: int
    title: str
    content: Optional[str]
    source_type: str
    file_name: Optional[str]
    tags: List[str]
    is_favorite: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MemoryList(BaseModel):
    items: List[MemoryOut]
    total: int


# ─────────────────────────────────────────────────────────────────────────────
# Search
# ─────────────────────────────────────────────────────────────────────────────

class SearchResult(BaseModel):
    memory_id: int
    title: str
    snippet: str              # first N chars of content
    source_type: str
    file_name: Optional[str]
    tags: List[str]
    score: float              # similarity score (lower distance = higher relevance)
    is_favorite: bool
    created_at: datetime


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    ai_summary: Optional[str]
    total: int


# ─────────────────────────────────────────────────────────────────────────────
# Tag / Favorite
# ─────────────────────────────────────────────────────────────────────────────

class TagUpdate(BaseModel):
    tags: List[str]


# ─────────────────────────────────────────────────────────────────────────────
# Search History
# ─────────────────────────────────────────────────────────────────────────────

class SearchHistoryOut(BaseModel):
    id: int
    query: str
    result_count: int
    searched_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────────────────────
# Stats
# ─────────────────────────────────────────────────────────────────────────────

class StatsOut(BaseModel):
    total_memories: int
    by_type: dict
    favorites: int
    recent_searches: List[SearchHistoryOut]
