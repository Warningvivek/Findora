# Mnemix Frontend

A high-end, Gen-Z style React frontend for the AI Memory Assistant 

## Tech Stack

| Layer | Tech |
|---|---|
| Framework | React 18 + Vite |
| Styling | Tailwind CSS v3 + custom CSS |
| Animations | Framer Motion |
| Icons | Lucide React |
| Routing | React Router v6 |
| HTTP | Axios |
| File uploads | React Dropzone |
| Toasts | React Hot Toast |

## Design System

- **Fonts**: Syne (display) + DM Sans (body)
- **Theme**: Deep black (`#050507`) with glassmorphism cards
- **Accents**: Electric violet (`#7c6aff`) + teal (`#00e5cc`) + coral (`#ff6b6b`)
- **Style**: Glassmorphism, subtle gradients, smooth motion

## Folder Structure

```
frontend/
├── index.html
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
├── package.json
├── .env.example
├── public/
│   └── favicon.svg
└── src/
    ├── main.jsx          # Entry point
    ├── App.jsx           # Router + providers
    ├── index.css         # Global styles + Tailwind
    ├── hooks/
    │   └── useAuth.jsx   # Auth context + hook
    ├── services/
    │   └── api.js        # Axios instance + all API calls
    ├── components/
    │   ├── MemoryCard.jsx   # Reusable memory card
    │   ├── EmptyState.jsx   # Empty states with SVG illustrations
    │   └── Skeleton.jsx     # Loading skeleton components
    └── pages/
        ├── AuthPage.jsx        # Login / Register
        ├── DashboardLayout.jsx # Sidebar shell
        ├── SearchPage.jsx      # Semantic search
        ├── UploadPage.jsx      # File upload + note writing
        ├── MemoriesPage.jsx    # All memories grid
        └── FavoritesPage.jsx   # Starred memories
```

## Setup

### 1. Prerequisites

- Node.js 18+ (check with `node -v`)
- Your FastAPI backend running on `http://localhost:8000`

### 2. Install dependencies

```bash
cd frontend
npm install
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env if your backend runs on a different port
```

### 4. Run in development

```bash
npm run dev
# Opens http://localhost:3000
```

### 5. Build for production

```bash
npm run build
# Output: dist/
npm run preview  # Preview the build locally
```

## Running with the Backend

Start **both** processes in separate terminals:

**Terminal 1 — Backend:**
```bash
cd ai-memory-assistant
uvicorn main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

Then open **http://localhost:3000** in your browser.

> The Vite dev server proxies `/api/*` requests to `http://localhost:8000`, so no CORS issues in development.

## API Endpoints Used

| Method | Endpoint | Used in |
|---|---|---|
| POST | `/api/auth/register` | AuthPage |
| POST | `/api/auth/login` | AuthPage |
| GET | `/api/memories` | MemoriesPage, FavoritesPage |
| POST | `/api/memories` | UploadPage |
| PATCH | `/api/memories/{id}/favorite` | All memory pages |
| DELETE | `/api/memories/{id}` | All memory pages |
| GET | `/api/search` | SearchPage |

## Features

- ✅ JWT auth with localStorage persistence
- ✅ Auto-redirect on 401 (token expiry)
- ✅ Drag & drop file uploads (PDF, images, TXT)
- ✅ Manual note writing interface
- ✅ Semantic search with AI summary display
- ✅ Filter by source type and max results
- ✅ Favorite / unfavorite memories
- ✅ Delete with confirmation
- ✅ Skeleton loading states
- ✅ Empty states with illustrations
- ✅ Fully responsive (mobile sidebar)
- ✅ Smooth Framer Motion animations
- ✅ Toast notifications
