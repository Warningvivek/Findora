# 🚀 Findora – AI Personal Memory Assistant

An intelligent, AI-powered memory system that lets you store, search, and interact with your personal data like ChatGPT.

Findora combines **semantic search, vector databases, and AI reasoning** to turn your files and notes into a smart, searchable knowledge base.

---

## 🧠 What Makes Findora Special?

Unlike basic note apps, Findora:

* Understands your data using **AI embeddings**
* Retrieves relevant context using **semantic search**
* Generates **human-like answers (ChatGPT-style)**
* Works with **PDFs, notes, and images**
* Runs fully with **Docker (production-ready)**

---

## ✨ Features

| Feature            | Description                           |
| ------------------ | ------------------------------------- |
| 🔐 Authentication  | JWT-based login/register system       |
| 📝 Memory Storage  | Save notes, PDFs, images              |
| 🔍 Semantic Search | FAISS + Sentence Transformers         |
| 🤖 AI Answers      | Context-aware, ChatGPT-like responses |
| 📄 OCR Support     | Extract text from images              |
| ⭐ Favorites        | Mark important memories               |
| 🏷️ Tags           | Organize your data                    |
| 📊 Dashboard       | Memory insights & stats               |
| 🔄 History         | Track recent searches                 |

---

## 🏗️ Architecture

```
Findora/
├── backend/
│   ├── core/            # Config & security
│   ├── database/        # Models & DB session
│   ├── routers/         # API endpoints
│   ├── services/        # AI logic (FAISS, summarization)
│
├── frontend/            # React UI
├── docker-compose.yml   # Deployment config
├── Dockerfile           # Backend container
└── nginx.conf           # Frontend server
```

---

## 🧠 How It Works

```text
User Query
   ↓
Vector Search (FAISS)
   ↓
Relevant Memories Retrieved
   ↓
AI Answer Generation (BART)
   ↓
ChatGPT-like Response
```

---

## 🚀 Run Locally (Docker)

### 1. Clone Repo

```bash
git clone https://github.com/Warningvivek/Findora
cd Findora
```

---

### 2. Start App

```bash
docker-compose up --build
```

---

### 3. Open

```
Frontend: http://localhost:3000
Backend Docs: http://localhost:8000/docs
```

---

## 🌍 Deployment (Render)

1. Push repo to GitHub
2. Go to Render → New Web Service
3. Select:

   * Environment: **Docker**
4. Add disk:

   ```
   Mount Path: /app
   ```
5. Deploy 🚀

---

## ⚙️ Environment Variables

```env
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite+aiosqlite:///./memory_assistant.db
EMBEDDING_MODEL=all-MiniLM-L6-v2
SUMMARIZER_MODEL=facebook/bart-large-cnn
UPLOAD_DIR=./uploads
FAISS_INDEX_DIR=./faiss_indexes
```

---

## 📡 API Overview

### Auth

* `POST /api/auth/register`
* `POST /api/auth/login`

### Memories

* `POST /api/memories/upload`
* `POST /api/memories/notes`
* `GET /api/memories`

### Search

* `GET /api/search?q=...`

---

## 🧠 AI Stack

* SentenceTransformers (Embeddings)
* FAISS (Vector DB)
* HuggingFace Transformers (BART)
* FastAPI (Backend)
* React + Tailwind (Frontend)
* Docker (Deployment)

---

## 🔒 Security

* Password hashing with bcrypt
* JWT authentication
* User data isolation
* File validation

---

## ⚠️ Limitations (Free Deployment)

* Cold start (Render free tier)
* Limited RAM for AI models
* Slower first request

---

## 🚀 Future Improvements

* Chat-style UI (like ChatGPT)
* LLM upgrade (Mistral / Llama)
* Better ranking (reranking models)
* Multi-document reasoning
* Cloud storage integration

---

## 👨‍💻 Author

**Vivek Kumar Singh**
Machine Learning Engineer | AI Developer

---

## ⭐ If you like this project

Give it a ⭐ on GitHub and support the work!

---
