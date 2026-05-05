"""
services/file_service.py
─────────────────────────
Handles file I/O and text extraction for all supported file types:
  • .pdf  → PyMuPDF
  • .txt  → plain read
  • .png / .jpg / .jpeg / .webp → pytesseract OCR
"""

import logging
import shutil
import uuid
from pathlib import Path
from typing import Optional, Tuple

from core.config import settings

logger = logging.getLogger(__name__)

# ── Allowed extensions ────────────────────────────────────────────────────────
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}
IMAGE_EXTENSIONS   = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}


def save_upload(file_bytes: bytes, original_filename: str, user_id: int) -> Path:
    """
    Persist uploaded bytes to disk under uploads/<user_id>/<uuid>_<filename>.
    Returns the full path.
    """
    user_dir = settings.UPLOAD_DIR / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(original_filename).suffix.lower()
    safe_name = f"{uuid.uuid4().hex}{ext}"
    dest = user_dir / safe_name
    dest.write_bytes(file_bytes)
    logger.debug("Saved upload %s → %s", original_filename, dest)
    return dest


def delete_file(file_path: str) -> None:
    """Remove a file from disk (silently ignore if missing)."""
    try:
        Path(file_path).unlink(missing_ok=True)
    except Exception as exc:
        logger.warning("Could not delete file %s: %s", file_path, exc)


def extract_text_from_pdf(path: Path) -> str:
    """Extract all text from a PDF using PyMuPDF."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(str(path))
        pages = [page.get_text() for page in doc]
        doc.close()
        return "\n".join(pages).strip()
    except Exception as exc:
        logger.error("PDF extraction failed for %s: %s", path, exc)
        return ""


def extract_text_from_image(path: Path) -> str:
    """Run Tesseract OCR on an image and return the extracted text."""
    try:
        import pytesseract
        from PIL import Image
        img = Image.open(str(path))
        text = pytesseract.image_to_string(img)
        return text.strip()
    except Exception as exc:
        logger.error("OCR failed for %s: %s", path, exc)
        return ""


def extract_text_from_txt(path: Path) -> str:
    """Read a plain-text file, trying UTF-8 then latin-1."""
    try:
        return path.read_text(encoding="utf-8").strip()
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1").strip()
    except Exception as exc:
        logger.error("TXT read failed for %s: %s", path, exc)
        return ""


def extract_text(file_path: str, source_type: str) -> str:
    """
    Dispatch text extraction based on source_type.
    source_type: 'pdf' | 'image' | 'txt'
    """
    path = Path(file_path)
    if not path.exists():
        logger.warning("File not found: %s", file_path)
        return ""

    if source_type == "pdf":
        return extract_text_from_pdf(path)
    elif source_type == "image":
        return extract_text_from_image(path)
    elif source_type == "txt":
        return extract_text_from_txt(path)
    else:
        return ""


def validate_file(filename: str, size_bytes: int) -> Tuple[bool, str]:
    """
    Return (ok, error_message).
    Checks extension allow-list and max file size.
    """
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"File type '{ext}' not supported. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"

    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if size_bytes > max_bytes:
        return False, f"File size exceeds {settings.MAX_FILE_SIZE_MB} MB limit"

    return True, ""


def detect_source_type(filename: str) -> str:
    """Map a filename extension to our source_type taxonomy."""
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return "pdf"
    elif ext == ".txt":
        return "txt"
    elif ext in IMAGE_EXTENSIONS:
        return "image"
    return "unknown"
