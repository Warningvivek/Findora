"""
database/models.py
──────────────────
SQLAlchemy ORM models for the AI Personal Digital Memory Assistant.
All tables follow a multi-tenant design: every row is scoped to a user_id.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean,
    ForeignKey, Float, JSON
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# ─────────────────────────────────────────────────────────────────────────────
# User
# ─────────────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    username      = Column(String(64),  unique=True, index=True, nullable=False)
    email         = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)
    created_at    = Column(DateTime, default=datetime.utcnow)
    is_active     = Column(Boolean, default=True)

    # Relationships
    memories      = relationship("Memory",       back_populates="owner", cascade="all, delete-orphan")
    searches      = relationship("SearchHistory", back_populates="user",  cascade="all, delete-orphan")


# ─────────────────────────────────────────────────────────────────────────────
# Memory  (core content unit)
# ─────────────────────────────────────────────────────────────────────────────

class Memory(Base):
    __tablename__ = "memories"

    id            = Column(Integer, primary_key=True, index=True)
    user_id       = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Content identity
    title         = Column(String(512), nullable=False)
    content       = Column(Text, nullable=True)   # extracted / entered text
    source_type   = Column(String(32),  nullable=False)  # note | pdf | txt | image
    file_path     = Column(String(1024), nullable=True)  # path on disk (files only)
    file_name     = Column(String(512),  nullable=True)

    # Metadata
    tags          = Column(JSON, default=list)    # list[str]
    is_favorite   = Column(Boolean, default=False)
    created_at    = Column(DateTime, default=datetime.utcnow)
    updated_at    = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Embedding reference (index position inside FAISS for this user)
    faiss_index   = Column(Integer, nullable=True)

    owner         = relationship("User", back_populates="memories")


# ─────────────────────────────────────────────────────────────────────────────
# Search History
# ─────────────────────────────────────────────────────────────────────────────

class SearchHistory(Base):
    __tablename__ = "search_history"

    id            = Column(Integer, primary_key=True, index=True)
    user_id       = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    query         = Column(String(1024), nullable=False)
    result_count  = Column(Integer, default=0)
    searched_at   = Column(DateTime, default=datetime.utcnow)

    user          = relationship("User", back_populates="searches")
