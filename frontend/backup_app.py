"""
frontend/app.py
────────────────
AI Personal Digital Memory Assistant – Streamlit Frontend

A sleek, production-quality UI with:
  • Auth (login / register)
  • Upload section (files + notes)
  • Semantic search with AI summary
  • Memory library browser
  • Favorites & tagging
  • Recent searches sidebar
"""

import streamlit as st
import requests
import json
from datetime import datetime
from typing import Optional

# ── Configuration ─────────────────────────────────────────────────────────────
API_BASE = "http://localhost:8000/api"

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MindVault – AI Memory",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* ── Typography & base ── */
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
  }

  /* ── Dark amber/ink palette ── */
  :root {
    --bg:         #0f0e0c;
    --surface:    #1a1814;
    --surface2:   #252218;
    --border:     #2e2a22;
    --accent:     #e8a838;
    --accent2:    #c47a2a;
    --text:       #f0ead8;
    --muted:      #8a8070;
    --danger:     #c0392b;
    --success:    #27ae60;
  }

  /* ── Sidebar ── */
  section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
  }

  /* ── Main background ── */
  .stApp {
    background: var(--bg) !important;
  }

  /* ── Cards ── */
  .memory-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 12px;
    transition: border-color 0.2s, box-shadow 0.2s;
    position: relative;
  }
  .memory-card:hover {
    border-color: var(--accent2);
    box-shadow: 0 4px 24px rgba(232,168,56,0.08);
  }
  .memory-card.favorite {
    border-left: 3px solid var(--accent);
  }

  /* ── Source badge ── */
  .badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-right: 6px;
  }
  .badge-note   { background: #1e3a5f; color: #7eb8f7; }
  .badge-pdf    { background: #3d1f1f; color: #f78080; }
  .badge-image  { background: #1f3d1f; color: #80f780; }
  .badge-txt    { background: #3d3520; color: #f7d880; }

  /* ── Score bar ── */
  .score-bar {
    height: 3px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    border-radius: 2px;
    margin-top: 8px;
  }

  /* ── AI Summary box ── */
  .ai-summary {
    background: linear-gradient(135deg, #1c1a12, #252218);
    border: 1px solid var(--accent2);
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 24px;
    position: relative;
  }
  .ai-summary::before {
    content: "✦ AI INSIGHT";
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.15em;
    color: var(--accent);
    display: block;
    margin-bottom: 10px;
  }

  /* ── Section headers ── */
  .section-title {
    font-family: 'DM Serif Display', serif;
    font-size: 28px;
    color: var(--text);
    margin-bottom: 4px;
  }
  .section-sub {
    color: var(--muted);
    font-size: 14px;
    margin-bottom: 24px;
  }

  /* ── Tag pills ── */
  .tag {
    display: inline-block;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 2px 8px;
    font-size: 12px;
    color: var(--muted);
    margin-right: 4px;
    margin-top: 4px;
  }

  /* ── Stat cards ── */
  .stat-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px 20px;
    text-align: center;
  }
  .stat-number {
    font-family: 'DM Serif Display', serif;
    font-size: 36px;
    color: var(--accent);
  }
  .stat-label {
    font-size: 12px;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
  }

  /* ── Streamlit overrides ── */
  .stTextInput > div > div > input,
  .stTextArea > div > div > textarea,
  .stSelectbox > div > div {
    background: var(--surface2) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
  }
  .stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.15s !important;
  }
  .stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
  }

  /* hide streamlit branding */
  #MainMenu { visibility: hidden; }
  footer    { visibility: hidden; }
  header    { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Session state helpers
# ─────────────────────────────────────────────────────────────────────────────

def init_session():
    defaults = {
        "token": None,
        "user": None,
        "page": "search",
        "last_search": None,
        "search_results": None,
        "ai_summary": None,
        "notification": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def set_notification(msg: str, kind: str = "success"):
    st.session_state.notification = {"msg": msg, "kind": kind}


def show_notification():
    n = st.session_state.get("notification")
    if n:
        if n["kind"] == "success":
            st.success(n["msg"])
        elif n["kind"] == "error":
            st.error(n["msg"])
        else:
            st.info(n["msg"])
        st.session_state.notification = None


# ─────────────────────────────────────────────────────────────────────────────
# API helpers
# ─────────────────────────────────────────────────────────────────────────────

def auth_headers() -> dict:
    return {"Authorization": f"Bearer {st.session_state.token}"}


def api_get(path: str, params: dict = None) -> Optional[dict]:
    try:
        r = requests.get(f"{API_BASE}{path}", headers=auth_headers(), params=params, timeout=30)
        if r.status_code == 200:
            return r.json()
        st.error(f"API error {r.status_code}: {r.text}")
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Cannot connect to the  Is it running on port 8000?")
    return None


def api_post(path: str, json_data: dict = None, files=None, data: dict = None) -> Optional[dict]:
    try:
        if files:
            r = requests.post(f"{API_BASE}{path}", headers=auth_headers(),
                              files=files, data=data, timeout=60)
        else:
            r = requests.post(f"{API_BASE}{path}", headers=auth_headers(),
                              json=json_data, timeout=30)
        if r.status_code in (200, 201):
            return r.json()
        st.error(f"API error {r.status_code}: {r.json().get('detail', r.text)}")
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Cannot connect to the ")
    return None


def api_delete(path: str) -> bool:
    try:
        r = requests.delete(f"{API_BASE}{path}", headers=auth_headers(), timeout=15)
        return r.status_code == 204
    except requests.exceptions.ConnectionError:
        return False


def api_patch(path: str, json_data: dict = None) -> Optional[dict]:
    try:
        r = requests.patch(f"{API_BASE}{path}", headers=auth_headers(),
                           json=json_data, timeout=15)
        if r.status_code == 200:
            return r.json()
    except requests.exceptions.ConnectionError:
        pass
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Auth pages
# ─────────────────────────────────────────────────────────────────────────────

def render_auth():
    """Render login / register form."""
    st.markdown("""
    <div style="text-align:center; padding: 40px 0 20px;">
      <div style="font-family:'DM Serif Display',serif; font-size:52px; color:#e8a838;">🧠 MindVault</div>
      <div style="color:#8a8070; font-size:16px; margin-top:8px;">Your AI-powered personal knowledge base</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        tab1, tab2 = st.tabs(["Sign In", "Create Account"])

        with tab1:
            with st.form("login_form"):
                st.markdown("### Welcome back")
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Sign In →", use_container_width=True)

            if submitted and username and password:
                with st.spinner("Authenticating…"):
                    r = requests.post(
                        f"{API_BASE}/auth/login",
                        json={"username": username, "password": password},
                        timeout=15,
                    )
                if r.status_code == 200:
                    data = r.json()
                    st.session_state.token = data["access_token"]
                    st.session_state.user  = data["user"]
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")

        with tab2:
            with st.form("register_form"):
                st.markdown("### Create your vault")
                new_username = st.text_input("Username", key="reg_user")
                new_email    = st.text_input("Email", key="reg_email")
                new_password = st.text_input("Password (min 6 chars)", type="password", key="reg_pass")
                submitted2   = st.form_submit_button("Create Account →", use_container_width=True)

            if submitted2 and new_username and new_email and new_password:
                with st.spinner("Creating account…"):
                    r = requests.post(
                        f"{API_BASE}/auth/register",
                        json={"username": new_username, "email": new_email, "password": new_password},
                        timeout=15,
                    )
                if r.status_code == 201:
                    st.success("Account created! Please sign in.")
                else:
                    st.error(r.json().get("detail", "Registration failed"))


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────

def render_sidebar():
    with st.sidebar:
        # Brand
        st.markdown("""
        <div style="padding:12px 0 20px; text-align:center;">
          <div style="font-family:'DM Serif Display',serif; font-size:26px; color:#e8a838;">🧠 MindVault</div>
          <div style="font-size:11px; color:#8a8070; letter-spacing:0.1em;">PERSONAL MEMORY AI</div>
        </div>
        """, unsafe_allow_html=True)

        user = st.session_state.user
        st.markdown(f"<div style='text-align:center; color:#8a8070; font-size:13px; margin-bottom:16px;'>@{user['username']}</div>", unsafe_allow_html=True)

        st.divider()

        # Navigation
        pages = {
            "🔍 Search": "search",
            "➕ Add Memory": "add",
            "📚 Library": "library",
            "⭐ Favorites": "favorites",
            "📊 Dashboard": "dashboard",
        }

        for label, page_id in pages.items():
            is_active = st.session_state.page == page_id
            if st.button(label, use_container_width=True, type="primary" if is_active else "secondary"):
                st.session_state.page = page_id
                st.rerun()

        st.divider()

        # Recent searches
        st.markdown("<div style='font-size:12px; color:#8a8070; letter-spacing:0.08em; margin-bottom:8px;'>RECENT SEARCHES</div>", unsafe_allow_html=True)
        history = api_get("/search/history", params={"limit": 6})
        if history:
            for item in history:
                q = item["query"]
                if st.button(f"↩ {q[:28]}…" if len(q) > 28 else f"↩ {q}",
                             key=f"hist_{item['id']}", use_container_width=True):
                    st.session_state.page = "search"
                    st.session_state.last_search = q
                    st.rerun()
        else:
            st.markdown("<div style='color:#8a8070; font-size:12px;'>No searches yet</div>", unsafe_allow_html=True)

        st.divider()

        if st.button("🚪 Sign Out", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Shared components
# ─────────────────────────────────────────────────────────────────────────────

SOURCE_ICONS = {"note": "📝", "pdf": "📄", "image": "🖼️", "txt": "📃"}
BADGE_CLASSES = {"note": "badge-note", "pdf": "badge-pdf", "image": "badge-image", "txt": "badge-txt"}


def render_memory_card(m: dict, show_score: bool = False, score: float = None):
    src  = m.get("source_type", "note")
    icon = SOURCE_ICONS.get(src, "📎")
    badge_cls = BADGE_CLASSES.get(src, "badge-note")
    fav  = m.get("is_favorite", False)

    tags_html = "".join(f'<span class="tag">{t}</span>' for t in (m.get("tags") or []))
    content   = m.get("content") or m.get("snippet") or ""
    snippet   = content[:200] + "…" if len(content) > 200 else content
    date_str  = m.get("created_at", "")[:10]

    score_html = ""
    if show_score and score is not None:
        pct = int(score * 100)
        score_html = f"""
        <div style="display:flex; align-items:center; gap:8px; margin-top:8px;">
          <div style="flex:1; height:3px; background:#2e2a22; border-radius:2px;">
            <div style="width:{pct}%; height:100%; background:linear-gradient(90deg,#e8a838,#c47a2a); border-radius:2px;"></div>
          </div>
          <span style="font-size:11px; color:#8a8070;">{pct}% match</span>
        </div>"""

    fav_star = "⭐" if fav else ""

    st.markdown(f"""
    <div class="memory-card {'favorite' if fav else ''}">
      <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <div>
          <span class="badge {badge_cls}">{icon} {src}</span>
          {fav_star}
          <div style="font-size:17px; font-weight:600; color:#f0ead8; margin-top:8px;">{m['title']}</div>
        </div>
        <div style="font-size:11px; color:#8a8070;">{date_str}</div>
      </div>
      <div style="color:#8a8070; font-size:14px; margin-top:8px; line-height:1.6;">{snippet}</div>
      {score_html}
      <div style="margin-top:10px;">{tags_html}</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 3])

    # Get ID safely once
    memory_id = m.get("id")

    # Fallback key (only for UI uniqueness)
    safe_key = memory_id if memory_id else f"temp_{hash(m.get('title', ''))}"

    with col1:
        if st.button("⭐" if not fav else "★ Un-fav", key=f"fav_{safe_key}_{show_score}"):

            if memory_id:
                api_patch(f"/memories/{memory_id}/favorite")
                set_notification("Favorite updated!")
            else:
                st.warning("Cannot favorite this item (missing ID)")

            st.rerun()


    with col2:
        if st.button("🗑 Delete", key=f"del_{safe_key}_{show_score}"):

            if memory_id:
                if api_delete(f"/memories/{memory_id}"):
                    set_notification("Memory deleted.")
            else:
                st.warning("Cannot delete this item (missing ID)")

            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Pages
# ─────────────────────────────────────────────────────────────────────────────

def page_search():
    st.markdown('<div class="section-title">Semantic Search</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Ask anything — your vault understands meaning, not just keywords</div>', unsafe_allow_html=True)

    show_notification()

    # Pre-fill from sidebar click
    default_q = st.session_state.get("last_search", "")

    col_input, col_btn = st.columns([5, 1])
    with col_input:
        query = st.text_input("", placeholder="e.g. machine learning projects I worked on…",
                              value=default_q, label_visibility="collapsed")
    with col_btn:
        search_clicked = st.button("Search →", type="primary", use_container_width=True)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        top_k = st.slider("Max results", 3, 20, 8)
    with col_b:
        filter_type = st.selectbox("Filter type", ["All", "note", "pdf", "txt", "image"])
    with col_c:
        ai_sum = st.checkbox("AI summary", value=True)

    if search_clicked and query.strip():
        st.session_state.last_search = query
        params = {"q": query, "top_k": top_k, "summarize": ai_sum}
        if filter_type != "All":
            params["source_type"] = filter_type

        with st.spinner("🔍 Searching your vault…"):
            data = api_get("/search", params=params)

        if data:
            st.session_state.search_results = data.get("results", [])
            st.session_state.ai_summary     = data.get("ai_summary")

    results   = st.session_state.get("search_results")
    ai_summary = st.session_state.get("ai_summary")

    if results is not None:
        if ai_summary:
            st.markdown(f"""
            <div class="ai-summary">
              <div style="color:#f0ead8; line-height:1.7; font-size:15px;">{ai_summary}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"**{len(results)} results**")
        if results:
            for r in results:
                render_memory_card(r, show_score=True, score=r.get("score", 0))
        else:
            st.info("No memories found for that query. Try adding some content first!")


def page_add():
    st.markdown('<div class="section-title">Add to Vault</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Store notes, documents, images — all searchable by meaning</div>', unsafe_allow_html=True)

    show_notification()

    tab1, tab2 = st.tabs(["✍️ Write a Note", "📎 Upload File"])

    with tab1:
        with st.form("note_form", clear_on_submit=True):
            title   = st.text_input("Title *", placeholder="e.g. Meeting notes – Q3 review")
            content = st.text_area("Content *", height=200, placeholder="Write anything you want to remember…")
            tags    = st.text_input("Tags (comma-separated)", placeholder="work, meeting, 2024")
            submitted = st.form_submit_button("💾 Save Note", type="primary", use_container_width=True)

        if submitted:
            if not title.strip() or not content.strip():
                st.error("Title and content are required.")
            else:
                tag_list = [t.strip() for t in tags.split(",") if t.strip()]
                with st.spinner("Indexing note…"):
                    result = api_post("/memories/notes", {
                        "title": title, "content": content, "tags": tag_list
                    })
                if result:
                    set_notification(f"✅ Note '{title}' saved to your vault!")
                    st.rerun()

    with tab2:
        with st.form("upload_form", clear_on_submit=True):
            uploaded   = st.file_uploader(
                "Choose a file",
                type=["pdf", "txt", "png", "jpg", "jpeg", "webp"],
                help="PDF, TXT, and images (OCR will extract text automatically)"
            )
            file_title = st.text_input("Title (optional — defaults to filename)")
            file_tags  = st.text_input("Tags (comma-separated)")
            submitted2 = st.form_submit_button("⬆️ Upload & Index", type="primary", use_container_width=True)

        if submitted2:
            if not uploaded:
                st.error("Please select a file.")
            else:
                tag_list = [t.strip() for t in file_tags.split(",") if t.strip()]
                files = {"file": (uploaded.name, uploaded.getvalue(), uploaded.type)}
                data  = {"tags": ",".join(tag_list)}
                if file_title:
                    data["title"] = file_title

                with st.spinner(f"Processing {uploaded.name}… (OCR may take a moment for images)"):
                    result = api_post("/memories/upload", files=files, data=data)
                if result:
                    set_notification(f"✅ '{uploaded.name}' indexed successfully!")
                    st.rerun()


def page_library():
    st.markdown('<div class="section-title">Memory Library</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Browse all your stored memories</div>', unsafe_allow_html=True)

    show_notification()

    col1, col2 = st.columns([2, 1])
    with col1:
        filter_type = st.selectbox("Filter by type", ["All", "note", "pdf", "txt", "image"])
    with col2:
        tag_filter = st.text_input("Filter by tag", placeholder="e.g. work")

    params = {"limit": 30}
    if filter_type != "All":
        params["source_type"] = filter_type
    if tag_filter:
        params["tag"] = tag_filter

    data = api_get("/memories", params=params)
    if not data:
        return

    items = data.get("items", [])
    total = data.get("total", 0)

    st.markdown(f"<div style='color:#8a8070; margin-bottom:16px;'>{total} total memories</div>", unsafe_allow_html=True)

    if not items:
        st.info("No memories yet. Go to 'Add Memory' to get started!")
        return

    for m in items:
        render_memory_card(m)


def page_favorites():
    st.markdown('<div class="section-title">Favorites</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Your starred memories</div>', unsafe_allow_html=True)

    show_notification()

    data = api_get("/memories", params={"favorites": "true", "limit": 50})
    if not data:
        return

    items = data.get("items", [])
    if not items:
        st.info("You haven't starred any memories yet. Click ⭐ on any memory to add it here.")
        return

    for m in items:
        render_memory_card(m)


def page_dashboard():
    st.markdown('<div class="section-title">Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Your vault at a glance</div>', unsafe_allow_html=True)

    show_notification()

    stats = api_get("/memories/stats")
    if not stats:
        return

    by_type   = stats.get("by_type", {})
    total     = stats.get("total_memories", 0)
    favorites = stats.get("favorites", 0)

    # ── Stat cards ─────────────────────────────────────────────────────────────
    cols = st.columns(5)
    stat_items = [
        ("Total", total, "🧠"),
        ("Notes", by_type.get("note", 0), "📝"),
        ("PDFs", by_type.get("pdf", 0), "📄"),
        ("Images", by_type.get("image", 0), "🖼️"),
        ("Favorites", favorites, "⭐"),
    ]
    for col, (label, val, icon) in zip(cols, stat_items):
        with col:
            st.markdown(f"""
            <div class="stat-card">
              <div style="font-size:24px;">{icon}</div>
              <div class="stat-number">{val}</div>
              <div class="stat-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Recent searches ────────────────────────────────────────────────────────
    searches = stats.get("recent_searches", [])
    if searches:
        st.markdown("### Recent Searches")
        for s in searches:
            q   = s["query"]
            cnt = s["result_count"]
            t   = s["searched_at"][:10]
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; padding:10px 16px;
                        background:#1a1814; border-radius:8px; margin-bottom:6px;">
              <span style="color:#f0ead8;">↩ {q}</span>
              <span style="color:#8a8070; font-size:12px;">{cnt} results · {t}</span>
            </div>
            """, unsafe_allow_html=True)

    # ── Quick actions ─────────────────────────────────────────────────────────
    st.markdown("### Quick Actions")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("➕ Add a Note", use_container_width=True):
            st.session_state.page = "add"
            st.rerun()
    with c2:
        if st.button("🔍 Search Vault", use_container_width=True):
            st.session_state.page = "search"
            st.rerun()
    with c3:
        if st.button("📚 Browse Library", use_container_width=True):
            st.session_state.page = "library"
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Main router
# ─────────────────────────────────────────────────────────────────────────────

def main():
    init_session()

    if not st.session_state.token:
        render_auth()
        return

    render_sidebar()

    page = st.session_state.page
    if page == "search":
        page_search()
    elif page == "add":
        page_add()
    elif page == "library":
        page_library()
    elif page == "favorites":
        page_favorites()
    elif page == "dashboard":
        page_dashboard()
    else:
        page_search()


if __name__ == "__main__":
    main()
