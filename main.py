"""
CRAG - Corrective Retrieval-Augmented Generation
Main Application Entrypoint & Authentication Portal
"""

import os
import json
import streamlit as st
import pyrebase
from dotenv import load_dotenv

import ui_styles
import rag_backend as rb

# Load environment configuration
load_dotenv(dotenv_path="./.env")

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="CRAG AI | Home",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply unified compact 1.0 viewpoint design system
ui_styles.apply_theme()

# --- Firebase Configuration ---
firebase_config = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.getenv("PROJECT_ID"),
    "messagingSenderId": os.getenv("MESSAGING_SENDER_ID"),
    "storageBucket": os.getenv("STORAGE_BUCKET"),
    "appId": os.getenv("APP_ID"),
    "measurementId": os.getenv("MEASUREMENT_ID"),
    "databaseURL": os.getenv("DATABASE_URL")
}


@st.cache_resource(show_spinner=False)
def init_firebase():
    """Initializes and returns the Firebase Auth object."""
    try:
        required_keys = ["apiKey", "authDomain", "projectId"]
        if not all(firebase_config.get(k) and firebase_config.get(k) != "your-firebase-api-key" for k in required_keys):
            return None
        firebase = pyrebase.initialize_app(firebase_config)
        return firebase.auth()
    except Exception as e:
        return None


auth = init_firebase()

# --- Session State Initialization ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "rag_components" not in st.session_state:
    st.session_state.rag_components = None
if "history" not in st.session_state:
    st.session_state.history = []

# --- Sidebar Content ---
ui_styles.render_sidebar_header()

if st.session_state.authenticated:
    ui_styles.render_user_profile(st.session_state.user)
    if st.session_state.rag_components:
        ui_styles.render_status_card(
            doc_name=st.session_state.rag_components.get("doc_name", "Document"),
            chunk_count=len(st.session_state.rag_components.get("chunks", []))
        )
    if st.sidebar.button("🚪 Logout Session", type="secondary", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.rag_components = None
        st.session_state.messages = []
        st.rerun()
else:
    st.sidebar.markdown(
        """
        <div style="background: rgba(15, 23, 42, 0.6); padding: 0.75rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08);">
            <div style="font-size: 0.75rem; font-weight: 700; color: #a5b4fc; margin-bottom: 0.25rem;">🔐 AUTHENTICATION REQUIRED</div>
            <p style="font-size: 0.72rem; color: #94a3b8; margin: 0; line-height: 1.35;">
                Sign in with your account or use <b>Guest Mode</b> to access the document Q&A engine.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Sidebar System Health Status
groq_ready = bool(os.getenv("GROQ_API_KEY"))
st.sidebar.markdown(
    f"""
    <div style="margin-top: 1rem; padding-top: 0.75rem; border-top: 1px solid rgba(255,255,255,0.06); font-size: 0.72rem; color: #64748b;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
            <span>Groq Engine:</span>
            <span style="color: {'#10b981' if groq_ready else '#ef4444'}; font-weight: 600;">{'● Connected' if groq_ready else '○ Missing Key'}</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
            <span>Model:</span>
            <span style="color: #a5b4fc; font-weight: 600;">{rb.GROQ_MODEL}</span>
        </div>
        <div style="display: flex; justify-content: space-between;">
            <span>Vector Index:</span>
            <span style="color: #10b981; font-weight: 600;">● FAISS IP</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# --- Authentication Form ---
def render_auth_portal():
    """Renders a sleek, compact authentication card."""
    col1, col2, col3 = st.columns([1, 1.8, 1])

    with col2:
        st.markdown(
            """
            <div class="crag-hero-container">
                <div class="crag-hero-badge">
                    <span class="crag-pulse-dot"></span>
                    CORRECTIVE RAG PLATFORM
                </div>
                <div class="crag-gradient-title">CRAG AI</div>
                <p class="crag-subtitle">
                    Contextual & Self-Correcting Retrieval-Augmented Generation for PDF Documents.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.container(border=True):
            action = st.radio(
                "Mode",
                ["Sign In", "Create Account"],
                horizontal=True,
                label_visibility="collapsed"
            )

            with st.form("auth_form", clear_on_submit=False):
                email = st.text_input("Email", placeholder="user@example.com")
                password = st.text_input("Password", type="password", placeholder="••••••••••••")
                
                submitted = st.form_submit_button(
                    label="Sign In →" if action == "Sign In" else "Create Account →",
                    type="primary",
                    use_container_width=True
                )

                if submitted:
                    if not email or not password:
                        st.error("Please enter both email and password.")
                    elif auth is None:
                        st.warning("Firebase is in local mode. Please use Guest Access below or verify .env configuration.")
                    else:
                        try:
                            with st.spinner("Authenticating..."):
                                if action == "Sign In":
                                    user = auth.sign_in_with_email_and_password(email, password)
                                    st.session_state.authenticated = True
                                    st.session_state.user = user
                                    st.toast("Welcome back!", icon="🎉")
                                    st.rerun()
                                else:
                                    user = auth.create_user_with_email_and_password(email, password)
                                    st.session_state.authenticated = True
                                    st.session_state.user = user
                                    st.toast("Account created successfully!", icon="🚀")
                                    st.rerun()
                        except Exception as e:
                            try:
                                error_data = e.args[1]
                                error_json = json.loads(error_data)
                                msg = error_json.get("error", {}).get("message", "")
                                if msg in ["EMAIL_NOT_FOUND", "INVALID_PASSWORD", "INVALID_LOGIN_CREDENTIALS"]:
                                    st.error("Invalid email or password. Please try again.")
                                elif msg == "EMAIL_EXISTS":
                                    st.error("An account with this email already exists. Switch to Sign In.")
                                elif msg == "WEAK_PASSWORD":
                                    st.error("Password must be at least 6 characters.")
                                else:
                                    st.error(f"Error: {msg}")
                            except Exception:
                                st.error("Authentication failed. Please verify credentials or use Guest Mode.")

            st.markdown(
                """
                <div style="display: flex; align-items: center; text-align: center; margin: 0.75rem 0;">
                    <div style="flex-grow: 1; height: 1px; background: rgba(255,255,255,0.08);"></div>
                    <span style="padding: 0 8px; color: #64748b; font-size: 0.7rem; text-transform: uppercase; font-weight: 600;">Or</span>
                    <div style="flex-grow: 1; height: 1px; background: rgba(255,255,255,0.08);"></div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button("🚀 Continue with Guest Access", type="secondary", use_container_width=True):
                st.session_state.authenticated = True
                st.session_state.user = {"email": "guest.user@crag.app"}
                st.toast("Signed in as Guest User!", icon="⚡")
                st.rerun()


# --- Logged-In User Dashboard ---
def render_authenticated_dashboard():
    """Renders the sleek, compact dashboard when authenticated."""
    user_email = st.session_state.user.get("email", "Explorer") if isinstance(st.session_state.user, dict) else "Explorer"
    username = user_email.split("@")[0].capitalize()

    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap;">
            <div>
                <h1 style="margin: 0; font-size: 1.6rem; font-weight: 800;">Welcome, {username}</h1>
                <p style="margin: 0; color: #94a3b8; font-size: 0.85rem;">Corrective RAG Document Analysis Workspace</p>
            </div>
            <div class="crag-hero-badge" style="margin: 0;">
                <span class="crag-pulse-dot"></span>
                ACTIVE SESSION
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Metric KPI Row
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.markdown(
            f"""
            <div class="crag-kpi-box">
                <div>
                    <div class="crag-kpi-label">Active Document</div>
                    <div class="crag-kpi-value" style="font-size: 1.05rem; margin-top: 0.2rem;">
                        {"📄 " + st.session_state.rag_components.get("doc_name", "None")[:18] + "..." if st.session_state.rag_components else "None Loaded"}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with kpi2:
        chunk_count = len(st.session_state.rag_components.get("chunks", [])) if st.session_state.rag_components else 0
        st.markdown(
            f"""
            <div class="crag-kpi-box">
                <div>
                    <div class="crag-kpi-label">Indexed Chunks</div>
                    <div class="crag-kpi-value" style="color: #a5b4fc;">{chunk_count}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with kpi3:
        queries_count = len(st.session_state.history)
        st.markdown(
            f"""
            <div class="crag-kpi-box">
                <div>
                    <div class="crag-kpi-label">Session Queries</div>
                    <div class="crag-kpi-value" style="color: #38bdf8;">{queries_count}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

    # Quick Navigation Cards
    nav1, nav2 = st.columns(2)

    with nav1:
        with st.container(border=True):
            st.markdown(
                """
                <div class="crag-card-icon">💬</div>
                <div class="crag-card-title">Chat with Document</div>
                <div class="crag-card-desc">
                    Upload any PDF, chunk with page preservation, and ask questions with streaming answers and confidence scores.
                </div>
                """,
                unsafe_allow_html=True
            )
            st.page_link("pages/crag_app.py", label="Open CRAG Chat →", icon="🤖", use_container_width=True)

    with nav2:
        with st.container(border=True):
            st.markdown(
                """
                <div class="crag-card-icon">📊</div>
                <div class="crag-card-title">Analytics & History</div>
                <div class="crag-card-desc">
                    Review past queries and answers, track retrieval accuracy, and export your session as CSV or Markdown.
                </div>
                """,
                unsafe_allow_html=True
            )
            st.page_link("pages/history.py", label="View History & Reports →", icon="📈", use_container_width=True)

    # Core Features Section
    st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown(
            """
            <div class="crag-card">
                <div style="font-size: 1.25rem; margin-bottom: 0.25rem;">🎯</div>
                <div class="crag-card-title">Corrective Gate</div>
                <div class="crag-card-desc">
                    Evaluates mathematical cosine similarity across FAISS embeddings to flag low-confidence retrievals and prevent hallucinations.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with f2:
        st.markdown(
            """
            <div class="crag-card">
                <div style="font-size: 1.25rem; margin-bottom: 0.25rem;">📑</div>
                <div class="crag-card-title">Page Attribution</div>
                <div class="crag-card-desc">
                    Every retrieved paragraph retains its exact source page metadata so you can inspect the exact excerpt used.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with f3:
        st.markdown(
            """
            <div class="crag-card">
                <div style="font-size: 1.25rem; margin-bottom: 0.25rem;">⚡</div>
                <div class="crag-card-title">Groq Inference</div>
                <div class="crag-card-desc">
                    Low-latency streaming token generation powered by Groq LPU infrastructure.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


# --- Main Controller ---
if not st.session_state.authenticated:
    render_auth_portal()
else:
    render_authenticated_dashboard()
