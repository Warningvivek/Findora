# 🧠 MindVault – AI Personal Digital Memory Assistant

A production-ready, multi-user knowledge management system with semantic search and AI-generated summaries.

---

## ✨ Features

| Feature | Details |
|---|---|
| **Multi-user auth** | JWT-based login/register, bcrypt hashed passwords |
| **Content types** | Text notes, PDFs, TXT files, Images (with OCR) |
| **Semantic search** | SentenceTransformers `all-MiniLM-L6-v2` + FAISS vector index |
| **AI summaries** | BART (`facebook/bart-large-cnn`) generates insights from results |
| **Tagging** | Free-form tag taxonomy per memory |
| **Favorites** | Star important memories for quick access |
| **Recent searches** | Sidebar history of past queries |
| **Dashboard** | Stats by type, favorites count, quick actions |
| **Per-user isolation** | Each user's data (DB rows + FAISS index) is fully isolated |

---

## 🏗️ Architecture

```
ai-memory-assistant/
├── main.py                         # FastAPI app entry point
├── requirements.txt
├── .env                            # Environment configuration
│
├── backend/
│   ├── core/
│   │   ├── config.py               # Pydantic settings
│   │   ├── security.py             # JWT + bcrypt utilities
│   │   └── dependencies.py         # get_current_user dependency
│   │
│   ├── database/
│   │   ├── models.py               # SQLAlchemy ORM models
│   │   └── session.py              # Async engine + session factory
│   │
│   ├── models/
│   │   └── schemas.py              # Pydantic request/response schemas
│   │
│   ├── routers/
│   │   ├── auth.py                 # /api/auth/*
│   │   ├── memories.py             # /api/memories/*
│   │   └── search.py               # /api/search/*
│   │
│   └── services/
│       ├── embedding_service.py    # SentenceTransformers + FAISS
│       ├── summarization_service.py # BART summarizer
│       ├── file_service.py         # PDF/TXT/image text extraction
│       └── memory_service.py       # CRUD business logic
│
├── frontend/
│   └── app.py                      # Streamlit UI
│
├── scripts/
│   ├── setup.sh                    # One-shot setup
│   ├── run_sh
│   └── run_frontend.sh
│
├── uploads/                        # User file storage (auto-created)
└── faiss_indexes/                  # Per-user FAISS indexes (auto-created)
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Tesseract OCR (for image text extraction):
  - **macOS**: `brew install tesseract`
  - **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`
  - **Windows**: [Download installer](https://github.com/UB-Mannheim/tesseract/wiki)

### 1. Clone and setup

```bash
git clone <repo-url>
cd ai-memory-assistant

# Create venv and install all dependencies
bash scripts/setup.sh
```

### 2. Configure environment

Edit `.env` if needed (defaults work out of the box for local development):

```env
SECRET_KEY=your-super-secret-key-change-in-production
DATABASE_URL=sqlite+aiosqlite:///./memory_assistant.db
EMBEDDING_MODEL=all-MiniLM-L6-v2
SUMMARIZER_MODEL=facebook/bart-large-cnn
```

### 3. Start the backend

```bash
bash scripts/run_sh
# → http://localhost:8000
# → API docs: http://localhost:8000/docs
```

### 4. Start the frontend (new terminal)

```bash
bash scripts/run_frontend.sh
# → http://localhost:8501
```

### 5. Open in browser

Navigate to **http://localhost:8501**, create an account, and start building your vault!

---

## 📡 API Reference

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Login, returns JWT |
| GET | `/api/auth/me` | Current user info |

### Memories

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/memories/notes` | Create text note |
| POST | `/api/memories/upload` | Upload PDF/TXT/image |
| GET | `/api/memories` | List memories (filterable) |
| GET | `/api/memories/stats` | Dashboard statistics |
| GET | `/api/memories/{id}` | Single memory |
| PATCH | `/api/memories/{id}/favorite` | Toggle favorite |
| PATCH | `/api/memories/{id}/tags` | Update tags |
| DELETE | `/api/memories/{id}` | Delete memory |

### Search

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/search?q=...` | Semantic search |
| GET | `/api/search/history` | Recent searches |

**Search params:** `q`, `top_k` (1–50), `source_type`, `summarize` (bool)

---

## ⚙️ Configuration

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | (required) | JWT signing key — change in production |
| `DATABASE_URL` | SQLite | Any SQLAlchemy async URL |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | SentenceTransformers model |
| `SUMMARIZER_MODEL` | `facebook/bart-large-cnn` | HuggingFace summarizer |
| `UPLOAD_DIR` | `./uploads` | File storage root |
| `FAISS_INDEX_DIR` | `./faiss_indexes` | FAISS index storage |
| `MAX_FILE_SIZE_MB` | `50` | Upload size limit |

---

## 🔒 Security Notes

- Passwords hashed with bcrypt (cost factor 12)
- JWT tokens expire after 7 days (configurable)
- File uploads validated by extension and size
- Each user's FAISS index is isolated by user ID
- All DB queries are scoped to the authenticated user

---

## 🔧 Production Deployment

For production, switch to PostgreSQL:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/mindvault
```

Install the async driver:
```bash
pip install asyncpg
```

Deploy with gunicorn:
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## 📦 Tech Stack

- **Backend**: FastAPI + SQLAlchemy (async) + SQLite/PostgreSQL
- **AI/ML**: SentenceTransformers, FAISS, HuggingFace Transformers (BART)
- **File Processing**: PyMuPDF (PDF), pytesseract (OCR), Pillow
- **Auth**: JWT (python-jose) + bcrypt (passlib)
- **Frontend**: Streamlit with custom CSS theming
