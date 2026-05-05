"""
services/summarization_service.py
───────────────────────────────────
Upgraded AI summarizer — ChatGPT-like conversational answers.

Key improvements over v1:
  • Top-ranked snippet gets priority — no more resume drowning birthday answers
  • Direct factual extraction for names/dates/contacts (no model needed)
  • Smart intent detection with broader keyword coverage
  • Conversational answer formatting instead of raw bullet dumps
  • Model only called when genuinely needed (complex/general queries)
  • Graceful fallback chain: extract → model → truncate
"""

import logging
import re
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# ── Lazy model loading ────────────────────────────────────────────────────────
_pipeline = None


def _get_pipeline():
    global _pipeline
    if _pipeline is None:
        from transformers import pipeline
        from core.config import settings

        logger.info("Loading model: %s", settings.SUMMARIZER_MODEL)
        task = (
            "text2text-generation"
            if "t5" in settings.SUMMARIZER_MODEL.lower()
            else "summarization"
        )
        _pipeline = pipeline(
            task,
            model=settings.SUMMARIZER_MODEL,
            tokenizer=settings.SUMMARIZER_MODEL,
            device=-1,
        )
    return _pipeline


# ── Intent detection ──────────────────────────────────────────────────────────

INTENT_MAP = {
    "birthday":       ["birthday", "born", "dob", "birth date", "bday"],
    "date":           ["date", "when", "year", "month", "day", "time", "schedule", "deadline"],
    "contact":        ["contact", "email", "phone", "mobile", "linkedin", "github", "address", "reach"],
    "projects":       ["project", "built", "created", "developed", "made", "portfolio", "app", "system"],
    "skills":         ["skill", "technology", "tech", "tools", "language", "stack", "know", "expertise", "proficient"],
    "experience":     ["experience", "work", "intern", "job", "role", "position", "company", "employer", "worked"],
    "education":      ["education", "degree", "college", "university", "study", "studied", "school", "graduate", "cgpa", "gpa"],
    "certifications": ["certif", "award", "achievement", "accomplish", "honor", "prize"],
    "name":           ["name", "who is", "who are", "full name", "person"],
    "summary":        ["summary", "about", "overview", "profile", "describe", "tell me about"],
    "definition":     ["what is", "what are", "explain", "define", "meaning", "describe what"],
}


def _detect_intent(query: str) -> str:
    q = query.lower()
    for intent, keywords in INTENT_MAP.items():
        if any(kw in q for kw in keywords):
            return intent
    return "general"


# ── Direct fact extractors ────────────────────────────────────────────────────

def _extract_dates_from_text(text: str, person_hint: str = "") -> List[str]:
    """
    Pull date patterns from text, optionally filtering lines mentioning a person.
    Returns list of found date strings with context.
    """
    # Common date patterns: DD/MM/YYYY, MM-DD-YYYY, Month DD YYYY, etc.
    date_pattern = re.compile(
        r"""
        (?:
            \d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}   # 10/03/2003 or 3-10-2003
            | \d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2}    # 2003/03/10
            | (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\.?\s+\d{1,2},?\s+\d{4}  # March 10, 2003
            | \d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\.?\s+\d{4}     # 10 March 2003
        )
        """,
        re.VERBOSE | re.IGNORECASE,
    )

    results = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        # If we have a person hint, prefer lines mentioning them
        if person_hint and person_hint.lower() in line.lower():
            dates = date_pattern.findall(line)
            if dates:
                results.append(line)
        elif date_pattern.search(line):
            results.append(line)

    return results


def _extract_emails(text: str) -> List[str]:
    return re.findall(r"[\w.\-+]+@[\w.\-]+\.\w+", text)


def _extract_phones(text: str) -> List[str]:
    return re.findall(r"(?:\+91[\s\-]?)?\d[\d\s\-]{9,13}\d", text)


def _extract_section(text: str, *section_names: str) -> str:
    name_pat = "|".join(re.escape(n) for n in section_names)
    pattern = rf"(?i)(?:^|\n)\s*(?:{name_pat})\s*[:\-]?\s*\n(.*?)(?=\n\s*[A-Z][A-Z\s]{{3,}}[:\-]?\s*\n|\Z)"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else ""


def _extract_bullet_items(block: str, max_items: int = 8) -> List[str]:
    items = []
    for line in block.split("\n"):
        line = re.sub(r"^[•\-\*\–\→]\s*", "", line.strip())
        line = re.sub(r"^\d+[\.\)]\s*", "", line)
        if len(line) > 8:
            items.append(line)
        if len(items) >= max_items:
            break
    return items


def _truncate(text: str, max_words: int = 400) -> str:
    words = text.split()
    return " ".join(words[:max_words]) if len(words) > max_words else text


# ── Conversational answer formatter ──────────────────────────────────────────

def _conversational_answer(intent: str, items: List[str], raw: str, query: str) -> str:
    """Format extracted data as a friendly conversational answer."""

    # Clean query for display
    q_display = query.strip().rstrip("?").strip()

    if not items and not raw:
        return ""

    templates = {
        "birthday":       "Here are the birthdays I found:",
        "date":           f"Here's what I found about '{q_display}':",
        "contact":        "Here are the contact details I found:",
        "projects":       "Here are the projects I found:",
        "skills":         "Here are the skills and technologies:",
        "experience":     "Here's the work experience:",
        "education":      "Here's the educational background:",
        "certifications": "Here are the certifications and achievements:",
        "name":           "Here's the name information I found:",
        "summary":        "Here's an overview:",
        "definition":     f"Here's what I found about '{q_display}':",
        "general":        f"Here's what I found for '{q_display}':",
    }

    intro = templates.get(intent, f"Here's what I found:")

    if items:
        bullets = "\n".join(f"• {item}" for item in items)
        return f"{intro}\n\n{bullets}"
    else:
        clean = raw.strip()[:500]
        return f"{intro}\n\n{clean}"


# ── Core: answer from top snippet first ──────────────────────────────────────

def _answer_from_snippets(query: str, snippets: List[dict], intent: str) -> str:
    """
    Try to answer directly from snippets without the model.
    Prioritises the highest-scored snippet (index 0).
    """

    # ── Birthday / date queries — direct line extraction ──────────────────
    if intent in ("birthday", "date"):
        # Extract person name from query if present
        # e.g. "Yalok birthday" → try "Yalok", "alok"
        name_hint = ""
        words = query.strip().split()
        for w in words:
            if w.lower() not in ("birthday", "born", "bday", "date", "dob", "when", "is", "the", "of", "what"):
                name_hint = w
                break

        found_lines = []
        for snippet in snippets:
            content = snippet.get("content") or snippet.get("snippet") or ""
            lines = _extract_dates_from_text(content, person_hint=name_hint)
            found_lines.extend(lines)
            if not lines:
                # Fallback: return lines containing the name hint
                if name_hint:
                    for line in content.split("\n"):
                        if name_hint.lower() in line.lower() and len(line.strip()) > 5:
                            found_lines.append(line.strip())

        # Deduplicate preserving order
        seen = set()
        unique_lines = []
        for l in found_lines:
            key = l.strip().lower()
            if key not in seen:
                seen.add(key)
                unique_lines.append(l.strip())

        if unique_lines:
            return _conversational_answer(intent, unique_lines, "", query)

    # ── Contact queries ───────────────────────────────────────────────────
    if intent == "contact":
        all_text = "\n".join(s.get("content", "") for s in snippets[:3])
        emails = _extract_emails(all_text)
        phones = _extract_phones(all_text)
        block = _extract_section(all_text, "Contact", "Contact Information", "Profile")
        parts = []
        if emails:
            parts.append(f"Email: {emails[0]}")
        if phones:
            parts.append(f"Phone: {phones[0].strip()}")
        if block:
            parts.append(block[:300])
        if parts:
            return _conversational_answer("contact", parts, "", query)

    # ── Structured section queries ────────────────────────────────────────
    section_map = {
        "projects":       ("Projects", "Key Projects", "Personal Projects", "Academic Projects"),
        "skills":         ("Skills", "Technical Skills", "Technologies", "Tech Stack", "Core Skills"),
        "experience":     ("Experience", "Work Experience", "Professional Experience", "Employment"),
        "education":      ("Education", "Academic Background", "Qualifications"),
        "certifications": ("Certifications", "Certificates", "Awards", "Achievements", "Honors"),
        "summary":        ("Profile", "Summary", "About", "Overview", "Objective"),
    }

    if intent in section_map:
        all_text = "\n\n".join(s.get("content", "") for s in snippets[:5])
        block = _extract_section(all_text, *section_map[intent])
        items = _extract_bullet_items(block) if block else []

        # For projects: also scan for tech-keyword lines
        if intent == "projects" and not items:
            tech_hints = r"(python|java|react|node|django|flask|sql|ml|ai|api|app|web|model|system|platform)"
            for line in all_text.split("\n"):
                line = line.strip()
                if len(line) > 15 and ("|" in line or re.search(tech_hints, line, re.I)):
                    items.append(re.sub(r"^[•\-\*]\s*", "", line))
                if len(items) >= 6:
                    break

        if items or block:
            return _conversational_answer(intent, items, block, query)

    return ""  # Signal: couldn't answer directly, try the model


# ── Model-based answering ─────────────────────────────────────────────────────

def _model_answer(query: str, snippets: List[dict]) -> str:
    """
    Use the loaded model to answer. Only called when direct extraction fails.
    Uses the TOP snippet primarily to avoid context pollution from unrelated docs.
    """
    # Use top 2 snippets max, sorted by score descending
    top = sorted(snippets, key=lambda s: s.get("score", s.get("similarity", 0)), reverse=True)[:2]
    context = "\n\n".join(s.get("content", "") for s in top).strip()

    if not context:
        return ""

    try:
        pipe = _get_pipeline()
        truncated = _truncate(context, max_words=350)

        prompt = (
            f"Answer the following question based ONLY on the context below. "
            f"Be concise, direct, and conversational. "
            f"If listing items, use bullet points. "
            f"Do NOT mention the model, documents, or context — just answer naturally.\n\n"
            f"Question: {query}\n\n"
            f"Context:\n{truncated}\n\n"
            f"Answer:"
        )

        result = pipe(prompt, max_length=200, min_length=20, do_sample=False, truncation=True)

        if isinstance(result, list) and result:
            raw = result[0].get("generated_text") or result[0].get("summary_text") or ""
            # Strip prompt echo
            if "Answer:" in raw:
                raw = raw.split("Answer:")[-1].strip()
            raw = raw.replace(prompt, "").strip()
            if len(raw) > 20:
                return raw

    except Exception as exc:
        logger.warning("Model answering failed: %s", exc)

    return ""


# ── Public API ────────────────────────────────────────────────────────────────

def summarize_text(text: str, max_length: int = 150, min_length: int = 30) -> str:
    """Summarize a single block of text (used when storing a memory)."""
    text = text.strip()
    if not text:
        return ""
    if len(text.split()) <= min_length:
        return text

    try:
        pipe = _get_pipeline()
        truncated = _truncate(text, max_words=450)
        result = pipe(
            truncated,
            max_length=max_length,
            min_length=min_length,
            do_sample=False,
            truncation=True,
        )
        return result[0]["summary_text"].strip()
    except Exception as exc:
        logger.warning("Summarization failed, returning truncation: %s", exc)
        return text[:300] + ("…" if len(text) > 300 else "")


def summarize_results(query: str, snippets: List[dict]) -> str:
    """
    Given a search query and ranked memory snippets, produce a clean
    conversational answer.

    Answer priority:
      1. Direct extraction from top-ranked snippet (fast, accurate for facts)
      2. Model inference on top 2 snippets (for complex questions)
      3. Return top snippet content truncated (always has something useful)
    """
    if not snippets:
        return ""

    # Sort by score so best match is always first
    ranked = sorted(
        snippets,
        key=lambda s: s.get("score", s.get("similarity", 0)),
        reverse=True,
    )

    intent = _detect_intent(query)
    logger.info("Query: %r → intent: %s", query, intent)

    # ── Step 1: Direct extraction ────────────────────────────────────────
    direct = _answer_from_snippets(query, ranked, intent)
    if direct:
        return direct

    # ── Step 2: Model inference (top snippets only) ──────────────────────
    model_ans = _model_answer(query, ranked)
    if model_ans:
        return model_ans

    # ── Step 3: Graceful fallback — top snippet content ──────────────────
    top_content = ranked[0].get("content") or ranked[0].get("snippet") or ""
    if top_content:
        preview = top_content.strip()[:400]
        return f"Here's what I found:\n\n{preview}" + ("…" if len(top_content) > 400 else "")

    return ""


def preload_model():
    """Force-load model at startup (call from main.py lifespan)."""
    try:
        _get_pipeline()
        logger.info("Summarization model preloaded ✓")
    except Exception as e:
        logger.warning("Model preload failed (non-fatal): %s", e)