#!/usr/bin/env bash
# scripts/setup.sh
# ─────────────────────────────────────────────────────────────────────────────
# One-shot setup script for the AI Personal Digital Memory Assistant.
# Run from the project root: bash scripts/setup.sh
# ─────────────────────────────────────────────────────────────────────────────

set -e

echo ""
echo "🧠  MindVault – AI Personal Digital Memory Assistant"
echo "════════════════════════════════════════════════════"
echo ""

# ── Python version check ─────────────────────────────────────────────────────
PYTHON=$(command -v python3 || command -v python)
PY_VERSION=$($PYTHON --version 2>&1 | awk '{print $2}')
echo "✓  Using Python $PY_VERSION at $PYTHON"

# ── Virtual environment ──────────────────────────────────────────────────────
if [ ! -d ".venv" ]; then
  echo "→  Creating virtual environment…"
  $PYTHON -m venv .venv
fi
source .venv/bin/activate
echo "✓  Virtual environment active"

# ── Upgrade pip ──────────────────────────────────────────────────────────────
pip install --upgrade pip --quiet

# ── Install requirements ──────────────────────────────────────────────────────
echo "→  Installing Python dependencies (this may take a few minutes)…"
pip install -r requirements.txt --quiet
echo "✓  Dependencies installed"

# ── Tesseract OCR ─────────────────────────────────────────────────────────────
echo ""
echo "⚠️  Tesseract OCR (for image text extraction) must be installed separately:"
echo "   macOS:  brew install tesseract"
echo "   Ubuntu: sudo apt-get install tesseract-ocr"
echo "   Windows: https://github.com/UB-Mannheim/tesseract/wiki"
echo ""

# ── .env check ────────────────────────────────────────────────────────────────
if [ ! -f ".env" ]; then
  cp .env.example .env 2>/dev/null || true
  echo "⚠️  Created .env from template. Edit SECRET_KEY before deploying to production."
fi

# ── Directories ───────────────────────────────────────────────────────────────
mkdir -p uploads faiss_indexes
echo "✓  Storage directories created"

echo ""
echo "════════════════════════════════════════════════════"
echo "✅  Setup complete!"
echo ""
echo "  Start the backend:   bash scripts/run_sh"
echo "  Start the frontend:  bash scripts/run_frontend.sh"
echo ""
