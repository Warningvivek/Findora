#!/usr/bin/env bash
# scripts/run_sh
# Run from project root: bash scripts/run_sh

set -e
source .venv/bin/activate 2>/dev/null || true

echo "🚀  Starting FastAPI backend on http://localhost:8000"
echo "   API docs: http://localhost:8000/docs"
echo ""

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
