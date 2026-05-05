"""
main.py
────────
FastAPI application entry point.
Registers all routers, runs DB init on startup, and configures CORS.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.session import init_db
from routers import auth, memories, search
from core.config import settings
from services.summarization_service import preload_model
# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────
from contextlib import asynccontextmanager
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AI Memory Assistant…")

    # ✅ Initialize DB
    await init_db()

    # 🔥 Run model preload in background (non-blocking)
    asyncio.create_task(asyncio.to_thread(preload_model))

    logger.info("Startup complete ✓")
    yield

    logger.info("Shutting down…")

# ── App factory ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="AI Personal Digital Memory Assistant",
    description="Store, retrieve, and semantically search your personal knowledge base.",
    version="1.0.0",
    lifespan=lifespan,
)


# ── CORS (allow Streamlit frontend) ──────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(memories.router)
app.include_router(search.router)


# ── Health check ─────────────────────────────────────────────────────────────
@app.get("/health", tags=["System"])
async def health():
    return {"status": "ok", "version": "1.0.0"}


# ── Run directly (dev mode) ───────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)