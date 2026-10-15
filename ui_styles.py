"""
CRAG UI Styles & Theme System
Provides a sleek, compact modern glassmorphic design system for Streamlit with dark aesthetics,
subtle glowing accents, micro-animations, clean typography, and a 1.0 zoom compact viewport.
"""

import streamlit as st


def apply_theme():
    """Injects high-end modern CSS styling across Streamlit components with a tight 1.0 viewport."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

        /* Root CSS Variables */
        :root {
            --bg-primary: #0a0d14;
            --bg-secondary: #0f1523;
            --bg-card: rgba(17, 24, 39, 0.7);
            --bg-card-hover: rgba(26, 36, 56, 0.85);
            --border-subtle: rgba(255, 255, 255, 0.08);
            --border-glow: rgba(99, 102, 241, 0.35);
            --accent-primary: #6366f1;
            --accent-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
            --accent-glow: 0 4px 20px -2px rgba(99, 102, 241, 0.25);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --text-dim: #64748b;
            --radius-lg: 12px;
            --radius-md: 8px;
            --radius-sm: 6px;
        }

        /* 1.0 Viewport & Compact Scaling */
        html, body, [class*="css"], .stApp {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
            color: var(--text-main);
            background-color: var(--bg-primary);
            font-size: 14px !important;
            line-height: 1.45 !important;
            zoom: 1.0 !important;
        }

        /* Reduce excessive default Streamlit top and lateral padding */
        [data-testid="stAppViewBlockContainer"] {
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            max-width: 1200px !important;
            margin: 0 auto !important;
        }

        /* Ambient radial gradient background */
        .stApp {
            background: 
                radial-gradient(circle at 15% 10%, rgba(99, 102, 241, 0.06) 0%, transparent 40%),
                radial-gradient(circle at 85% 90%, rgba(6, 182, 212, 0.05) 0%, transparent 40%),
                var(--bg-primary) !important;
            background-attachment: fixed !important;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0d121f 0%, #080b12 100%) !important;
            border-right: 1px solid var(--border-subtle) !important;
        }

        [data-testid="stSidebarContent"] {
            padding: 1rem 0.75rem !important;
        }

        /* Top Header */
        header[data-testid="stHeader"] {
            background: rgba(10, 13, 20, 0.75) !important;
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
            border-bottom: 1px solid var(--border-subtle);
            height: 3rem !important;
        }

        /* Headings */
        h1 {
            color: #ffffff !important;
            font-weight: 800 !important;
            font-size: 1.75rem !important;
            letter-spacing: -0.025em !important;
            margin-bottom: 0.5rem !important;
        }

        h2 {
            color: #ffffff !important;
            font-weight: 700 !important;
            font-size: 1.35rem !important;
            margin-bottom: 0.4rem !important;
        }

        h3 {
            color: #ffffff !important;
            font-weight: 600 !important;
            font-size: 1.1rem !important;
            margin-bottom: 0.35rem !important;
        }

        /* Card Container (Streamlit vertical border wrappers) */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: var(--bg-card) !important;
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: var(--radius-lg) !important;
            padding: 1.15rem !important;
            box-shadow: 0 4px 20px -5px rgba(0, 0, 0, 0.4) !important;
            transition: all 0.2s ease !important;
            margin-bottom: 0.75rem !important;
        }

        [data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color: var(--border-glow) !important;
        }

        /* Compact Hero Block */
        .crag-hero-container {
            text-align: center;
            padding: 0.75rem 0.5rem;
            margin-bottom: 0.75rem;
            position: relative;
        }

        .crag-hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.25rem 0.65rem;
            border-radius: 9999px;
            background: rgba(99, 102, 241, 0.12);
            border: 1px solid rgba(99, 102, 241, 0.3);
            color: #a5b4fc;
            font-size: 0.72rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 0.5rem;
        }

        .crag-pulse-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background-color: #10b981;
            box-shadow: 0 0 6px #10b981;
            animation: pulse-ring 2s infinite;
        }

        @keyframes pulse-ring {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.4; transform: scale(1.2); }
        }

        .crag-gradient-title {
            font-size: 2rem;
            font-weight: 800;
            line-height: 1.2;
            background: linear-gradient(135deg, #ffffff 30%, #a5b4fc 70%, #38bdf8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.35rem;
        }

        .crag-subtitle {
            font-size: 0.95rem;
            color: var(--text-muted);
            max-width: 600px;
            margin: 0 auto;
            line-height: 1.45;
        }

        /* Feature Cards */
        .crag-card {
            background: rgba(17, 24, 39, 0.65);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
            padding: 1rem 1.15rem;
            transition: all 0.25s ease;
        }

        .crag-card:hover {
            border-color: rgba(99, 102, 241, 0.4);
            transform: translateY(-2px);
            background: rgba(23, 32, 54, 0.75);
        }

        .crag-card-icon {
            font-size: 1.5rem;
            margin-bottom: 0.4rem;
        }

        .crag-card-title {
            font-size: 1rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 0.25rem;
        }

        .crag-card-desc {
            font-size: 0.82rem;
            color: var(--text-muted);
            line-height: 1.4;
        }

        /* Compact KPI Box */
        .crag-kpi-box {
            background: rgba(15, 23, 42, 0.65);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 0.75rem 1rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .crag-kpi-value {
            font-size: 1.4rem;
            font-weight: 800;
            color: #ffffff;
            line-height: 1.2;
        }

        .crag-kpi-label {
            font-size: 0.72rem;
            color: var(--text-dim);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
        }

        /* Buttons Styling */
        .stButton>button {
            border-radius: var(--radius-md) !important;
            font-weight: 600 !important;
            padding: 0.45rem 1rem !important;
            font-size: 0.88rem !important;
            transition: all 0.2s ease !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }

        .stButton>button[kind="primary"], .stButton>button[data-testid="baseButton-primary"] {
            background: var(--accent-gradient) !important;
            color: #ffffff !important;
            border: none !important;
            box-shadow: 0 2px 10px -1px rgba(99, 102, 241, 0.4) !important;
        }

        .stButton>button[kind="primary"]:hover, .stButton>button[data-testid="baseButton-primary"]:hover {
            transform: translateY(-1px) !important;
            filter: brightness(1.1) !important;
        }

        .stButton>button[kind="secondary"], .stButton>button[data-testid="baseButton-secondary"] {
            background: rgba(30, 41, 59, 0.6) !important;
            color: #cbd5e1 !important;
        }

        .stButton>button[kind="secondary"]:hover, .stButton>button[data-testid="baseButton-secondary"]:hover {
            background: rgba(51, 65, 85, 0.8) !important;
            color: #ffffff !important;
        }

        /* Inputs and Text Areas */
        .stTextInput>div>div>input, 
        .stTextArea textarea,
        .stSelectbox>div>div {
            background-color: rgba(15, 23, 42, 0.8) !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            border-radius: var(--radius-md) !important;
            color: #f1f5f9 !important;
            font-size: 0.88rem !important;
            padding: 0.45rem 0.75rem !important;
        }

        .stTextInput>div>div>input:focus, 
        .stTextArea textarea:focus {
            border-color: #6366f1 !important;
            box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.25) !important;
        }

        /* Compact Chat Bubbles */
        [data-testid="stChatMessage"] {
            background-color: rgba(17, 24, 39, 0.6) !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: var(--radius-lg) !important;
            padding: 0.85rem 1.15rem !important;
            margin-bottom: 0.65rem !important;
            box-shadow: 0 2px 12px -3px rgba(0, 0, 0, 0.3) !important;
            font-size: 0.9rem !important;
            line-height: 1.5 !important;
        }

        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.7) 100%) !important;
            border-left: 3px solid #38bdf8 !important;
        }

        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
            background: linear-gradient(135deg, rgba(23, 30, 46, 0.7) 0%, rgba(17, 24, 39, 0.8) 100%) !important;
            border-left: 3px solid #818cf8 !important;
        }

        /* Chat Input Box */
        [data-testid="stChatInput"] {
            background-color: rgba(15, 23, 42, 0.95) !important;
            border: 1px solid rgba(99, 102, 241, 0.3) !important;
            border-radius: var(--radius-lg) !important;
        }

        /* File Uploader Container */
        [data-testid="stFileUploader"] {
            background: rgba(15, 23, 42, 0.5);
            border: 1px dashed rgba(99, 102, 241, 0.35);
            border-radius: var(--radius-md);
            padding: 0.75rem;
        }

        /* Expanders */
        [data-testid="stExpander"] {
            background: rgba(15, 23, 42, 0.6) !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: var(--radius-md) !important;
            margin-bottom: 0.5rem !important;
        }

        [data-testid="stExpander"] summary {
            font-size: 0.85rem !important;
            color: #cbd5e1 !important;
            padding: 0.4rem 0.75rem !important;
        }

        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: #0a0d14;
        }
        ::-webkit-scrollbar-thumb {
            background: #1e293b;
            border-radius: 3px;
        }

        /* User Profile Pill in Sidebar */
        .user-profile-badge {
            display: flex;
            align-items: center;
            gap: 0.6rem;
            padding: 0.5rem 0.75rem;
            background: rgba(30, 41, 59, 0.5);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            margin-bottom: 0.75rem;
        }

        .user-avatar {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            background: var(--accent-gradient);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            color: #fff;
            font-size: 0.8rem;
        }

        .user-email {
            font-size: 0.8rem;
            font-weight: 600;
            color: #f1f5f9;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .user-status {
            font-size: 0.7rem;
            color: #10b981;
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }

        /* Source Pills & Box */
        .source-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            padding: 0.2rem 0.5rem;
            border-radius: 5px;
            font-size: 0.72rem;
            font-weight: 600;
            background: rgba(99, 102, 241, 0.15);
            color: #a5b4fc;
            border: 1px solid rgba(99, 102, 241, 0.25);
            margin-right: 0.35rem;
            margin-bottom: 0.35rem;
        }

        .source-content-box {
            background: rgba(10, 15, 28, 0.6);
            border-left: 2px solid #6366f1;
            padding: 0.5rem 0.75rem;
            border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            color: #cbd5e1;
            margin-top: 0.35rem;
            line-height: 1.4;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_header():
    """Renders sleek branding in the sidebar."""
    st.sidebar.markdown(
        """
        <div style="padding-bottom: 0.65rem; border-bottom: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 0.85rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.35rem;">⚡</span>
                <div>
                    <h2 style="margin: 0; font-size: 1.15rem; font-weight: 800; background: linear-gradient(135deg, #ffffff, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">CRAG AI</h2>
                    <p style="margin: 0; font-size: 0.68rem; color: #94a3b8; letter-spacing: 0.04em;">CORRECTIVE RAG ENGINE</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_user_profile(user_info=None):
    """Renders a user profile badge in the sidebar with logout capability."""
    if user_info and isinstance(user_info, dict) and "email" in user_info:
        email = user_info["email"]
        initial = email[0].upper() if email else "U"
    else:
        email = "Active User"
        initial = "A"

    st.sidebar.markdown(
        f"""
        <div class="user-profile-badge">
            <div class="user-avatar">{initial}</div>
            <div class="user-info">
                <div class="user-email">{email}</div>
                <div class="user-status">
                    <span style="width: 5px; height: 5px; border-radius: 50%; background: #10b981; display: inline-block;"></span>
                    Authenticated
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status_card(doc_name, chunk_count):
    """Renders a live document status card in the sidebar."""
    st.sidebar.markdown(
        f"""
        <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 0.65rem; margin-top: 0.75rem;">
            <div style="font-size: 0.68rem; color: #64748b; text-transform: uppercase; font-weight: 700; margin-bottom: 0.35rem; letter-spacing: 0.04em;">Indexed Knowledge Base</div>
            <div style="font-size: 0.82rem; font-weight: 600; color: #f8fafc; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 0.25rem;">
                📄 {doc_name}
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.72rem; color: #94a3b8;">
                <span>Chunks: <b style="color: #a5b4fc;">{chunk_count}</b></span>
                <span>Engine: <b style="color: #38bdf8;">FAISS IP</b></span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
