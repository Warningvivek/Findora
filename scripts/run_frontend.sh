#!/usr/bin/env bash
# scripts/run_frontend.sh
# Run from project root: bash scripts/run_frontend.sh

set -e
source .venv/bin/activate 2>/dev/null || true

echo "🎨  Starting Streamlit frontend on http://localhost:8501"
echo ""

streamlit run frontend/app.py \
  --server.port 8501 \
  --server.address localhost \
  --theme.base dark \
  --theme.primaryColor "#e8a838" \
  --theme.backgroundColor "#0f0e0c" \
  --theme.secondaryBackgroundColor "#1a1814" \
  --theme.textColor "#f0ead8"
