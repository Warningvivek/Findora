"""
services/embedding_service.py
──────────────────────────────
Handles:
  • Text → embedding via SentenceTransformers
  • Per-user FAISS flat-L2 index (persisted to disk)
  • Add / search / delete vectors

Each user gets their own FAISS index file:
  <FAISS_INDEX_DIR>/<user_id>.index
  <FAISS_INDEX_DIR>/<user_id>.meta.json   ← maps FAISS row → memory_id
"""

import json
import logging
import os
from pathlib import Path
from typing import List, Tuple

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from core.config import settings

logger = logging.getLogger(__name__)

# ── Singleton model (loaded once per process) ─────────────────────────────────
_model: SentenceTransformer | None = None


def get_embedding_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info("Loading embedding model: %s", settings.EMBEDDING_MODEL)
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _model


# ── Helpers ───────────────────────────────────────────────────────────────────

def _index_path(user_id: int) -> Path:
    return settings.FAISS_INDEX_DIR / f"{user_id}.index"


def _meta_path(user_id: int) -> Path:
    return settings.FAISS_INDEX_DIR / f"{user_id}.meta.json"


def _load_meta(user_id: int) -> List[int]:
    """Return ordered list of memory_ids that map to FAISS row positions."""
    path = _meta_path(user_id)
    if path.exists():
        return json.loads(path.read_text())
    return []


def _save_meta(user_id: int, meta: List[int]) -> None:
    _meta_path(user_id).write_text(json.dumps(meta))


def _load_index(user_id: int, dim: int = 384) -> faiss.IndexFlatL2:
    """Load existing FAISS index or create a fresh one."""
    path = _index_path(user_id)
    if path.exists():
        return faiss.read_index(str(path))
    index = faiss.IndexFlatL2(dim)
    return index


def _save_index(user_id: int, index: faiss.IndexFlatL2) -> None:
    faiss.write_index(index, str(_index_path(user_id)))


# ── Public API ────────────────────────────────────────────────────────────────

def embed_text(text: str) -> np.ndarray:
    """Convert text → float32 embedding vector (shape: [dim])."""
    model = get_embedding_model()
    vec = model.encode([text], convert_to_numpy=True, normalize_embeddings=True)
    return vec[0].astype("float32")


def add_to_index(user_id: int, memory_id: int, text: str) -> int:
    """
    Embed `text` and add to the user's FAISS index.
    Returns the FAISS row index assigned to this vector.
    """
    vec = embed_text(text)
    index = _load_index(user_id, dim=len(vec))
    meta  = _load_meta(user_id)

    index.add(vec.reshape(1, -1))
    row = index.ntotal - 1      # 0-based position just added
    meta.append(memory_id)

    _save_index(user_id, index)
    _save_meta(user_id, meta)
    logger.debug("Added memory %d to user %d index (row %d)", memory_id, user_id, row)
    return row


def search_index(user_id: int, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
    """
    Semantic search in the user's FAISS index.
    Returns list of (memory_id, distance) sorted by ascending distance (closer = better).
    """
    path = _index_path(user_id)
    if not path.exists():
        return []

    vec   = embed_text(query)
    index = _load_index(user_id, dim=len(vec))
    meta  = _load_meta(user_id)

    if index.ntotal == 0:
        return []

    k = min(top_k, index.ntotal)
    distances, indices = index.search(vec.reshape(1, -1), k)

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx == -1:          # FAISS padding sentinel
            continue
        if idx < len(meta):
            results.append((meta[idx], float(dist)))
    return results


def remove_from_index(user_id: int, memory_id: int) -> None:
    """
    Mark a memory as deleted by rebuilding the index without its vector.
    Note: FAISS FlatL2 doesn't support in-place deletion; we rebuild.
    """
    path = _index_path(user_id)
    if not path.exists():
        return

    meta  = _load_meta(user_id)
    if memory_id not in meta:
        return

    old_index = _load_index(user_id)
    keep_rows = [i for i, mid in enumerate(meta) if mid != memory_id]

    if not keep_rows:
        # Wipe the index entirely
        path.unlink(missing_ok=True)
        _meta_path(user_id).unlink(missing_ok=True)
        return

    # Extract surviving vectors and rebuild
    all_vecs = old_index.reconstruct_n(0, old_index.ntotal)   # shape [n, dim]
    kept_vecs = np.stack([all_vecs[r] for r in keep_rows])
    new_meta  = [meta[r] for r in keep_rows]

    dim = kept_vecs.shape[1]
    new_index = faiss.IndexFlatL2(dim)
    new_index.add(kept_vecs)

    _save_index(user_id, new_index)
    _save_meta(user_id, new_meta)
    logger.debug("Removed memory %d from user %d index", memory_id, user_id)
