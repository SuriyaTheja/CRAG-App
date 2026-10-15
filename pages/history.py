"""
CRAG Analytics & History Dashboard
Inspect query histories, track retrieval confidence distributions, and export research reports.
"""

import sys
import os
import json
import pandas as pd
import streamlit as st

# Add workspace root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ui_styles

# --- Page Configuration ---
st.set_page_config(
    page_title="CRAG AI | History & Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply global design system
ui_styles.apply_theme()

# --- Page Protection Guard ---
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.markdown(
        """
        <div class="crag-hero-container">
            <div class="crag-hero-badge">🔒 ACCESS RESTRICTED</div>
            <div class="crag-gradient-title" style="font-size: 1.6rem;">Authentication Required</div>
            <p class="crag-subtitle">Please sign in to view your research session history and analytics.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.page_link("main.py", label="← Return to Login Portal", icon="🔑", use_container_width=True)
    st.stop()

# --- Sidebar Controls ---
ui_styles.render_sidebar_header()
ui_styles.render_user_profile(st.session_state.user)

if st.session_state.get("rag_components"):
    rc = st.session_state.rag_components
    ui_styles.render_status_card(
        doc_name=rc.get("doc_name", "Document"),
        chunk_count=len(rc.get("chunks", []))
    )

st.sidebar.markdown("### 🗂️ Navigation")
st.sidebar.page_link("main.py", label="Home Portal", icon="🏠")
st.sidebar.page_link("pages/crag_app.py", label="Document Chat", icon="💬")

# History data check
history_data = st.session_state.get("history", [])

# --- Main Dashboard Header ---
st.markdown(
    """
    <div style="margin-bottom: 0.75rem;">
        <h1 style="margin: 0; font-size: 1.6rem; font-weight: 800;">Analytics & Query History</h1>
        <p style="margin: 0.2rem 0 0 0; color: #94a3b8; font-size: 0.85rem;">
            Audit question-answering interactions, examine model citations, and export session logs.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

if not history_data:
    st.markdown(
        """
        <div class="crag-card" style="text-align: center; padding: 2rem 1.5rem; margin: 1rem 0;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📋</div>
            <div class="crag-card-title" style="font-size: 1.25rem;">No Queries in Active Session</div>
            <p class="crag-card-desc" style="max-width: 480px; margin: 0.25rem auto 1rem auto;">
                Ask questions about your uploaded documents in the CRAG Chat engine to build an interactive query timeline and analytics report.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.page_link("pages/crag_app.py", label="Go to CRAG Chat →", icon="🤖", use_container_width=True)
    st.stop()


# Convert to DataFrame
df = pd.DataFrame(history_data)

# --- KPI Metric Cards ---
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

total_queries = len(df)
unique_docs = df["Document"].nunique() if "Document" in df else 1

avg_words = int(df["Answer"].apply(lambda x: len(str(x).split())).mean()) if "Answer" in df else 0

if "Confidence" in df:
    high_conf_pct = f"{(df['Confidence'] == 'HIGH').mean():.0%}"
else:
    high_conf_pct = "N/A"

with kpi1:
    st.markdown(
        f"""
        <div class="crag-kpi-box">
            <div>
                <div class="crag-kpi-label">Total Queries</div>
                <div class="crag-kpi-value" style="color: #6366f1;">{total_queries}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
with kpi2:
    st.markdown(
        f"""
        <div class="crag-kpi-box">
            <div>
                <div class="crag-kpi-label">Documents Queried</div>
                <div class="crag-kpi-value" style="color: #38bdf8;">{unique_docs}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
with kpi3:
    st.markdown(
        f"""
        <div class="crag-kpi-box">
            <div>
                <div class="crag-kpi-label">Avg Answer Length</div>
                <div class="crag-kpi-value" style="color: #a5b4fc;">{avg_words} <span style="font-size: 0.85rem; font-weight: 500; color: #94a3b8;">words</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
with kpi4:
    st.markdown(
        f"""
        <div class="crag-kpi-box">
            <div>
                <div class="crag-kpi-label">High Confidence Ratio</div>
                <div class="crag-kpi-value" style="color: #10b981;">{high_conf_pct}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

# --- Confidence Distribution Breakdown ---
if "Confidence" in df:
    high_count = (df["Confidence"] == "HIGH").sum()
    med_count = (df["Confidence"] == "MEDIUM").sum()
    low_count = (df["Confidence"] == "LOW").sum()
    
    with st.expander("📊 Retrieval Confidence Breakdown", expanded=False):
        c_col1, c_col2, c_col3 = st.columns(3)
        c_col1.metric("🟢 High Confidence (Direct Grounding)", f"{high_count} queries", f"{(high_count/total_queries):.0%}")
        c_col2.metric("🟡 Medium Confidence (Partial Coverage)", f"{med_count} queries", f"{(med_count/total_queries):.0%}")
        c_col3.metric("🔴 Low Confidence (Corrective Fallback)", f"{low_count} queries", f"{(low_count/total_queries):.0%}")

# --- Filters & Search Bar ---
filter_col1, filter_col2, filter_col3, filter_col4 = st.columns([1.5, 1, 1, 1])

with filter_col1:
    search_term = st.text_input("🔍 Search History", placeholder="Filter by keywords...", label_visibility="collapsed")

with filter_col2:
    conf_filter = st.selectbox(
        "Confidence",
        ["All Confidences", "HIGH", "MEDIUM", "LOW"],
        label_visibility="collapsed"
    )

with filter_col3:
    doc_options = ["All Documents"] + list(df["Document"].unique()) if "Document" in df else ["All Documents"]
    doc_filter = st.selectbox("Document", doc_options, label_visibility="collapsed")

with filter_col4:
    view_mode = st.radio("View", ["Cards", "Table"], horizontal=True, label_visibility="collapsed")

# Apply filters
filtered_df = df.copy()

if search_term:
    search_mask = (
        filtered_df["Query"].str.contains(search_term, case=False, na=False) |
        filtered_df["Answer"].str.contains(search_term, case=False, na=False)
    )
    filtered_df = filtered_df[search_mask]

if conf_filter != "All Confidences":
    if "Confidence" in filtered_df:
        filtered_df = filtered_df[filtered_df["Confidence"] == conf_filter]

if doc_filter != "All Documents":
    if "Document" in filtered_df:
        filtered_df = filtered_df[filtered_df["Document"] == doc_filter]

st.markdown(f"<p style='color: #94a3b8; font-size: 0.78rem; margin: 0.25rem 0 0.75rem 0;'>Showing <b>{len(filtered_df)}</b> of <b>{len(df)}</b> interaction(s)</p>", unsafe_allow_html=True)


# --- Content Presentation ---
if view_mode == "Cards":
    for idx, row in filtered_df.iloc[::-1].iterrows():
        conf = row.get("Confidence", "HIGH")
        if conf == "HIGH":
            badge_color = "#10b981"
            badge_text = "🟢 High Match"
        elif conf == "MEDIUM":
            badge_color = "#f59e0b"
            badge_text = "🟡 Partial Match"
        else:
            badge_color = "#ef4444"
            badge_text = "🔴 Low Match"

        sim_score = row.get("Max_Similarity", "N/A")
        timestamp = row.get("Timestamp", "")
        doc_name = row.get("Document", "Unknown")
        latency = row.get("Latency_ms", "")

        with st.container(border=True):
            st.markdown(
                f"""
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; flex-wrap: wrap; gap: 0.35rem;">
                    <div style="display: flex; gap: 0.4rem; align-items: center;">
                        <span class="source-pill" style="margin: 0;">📄 {doc_name}</span>
                        <span style="font-size: 0.72rem; color: #64748b;">🕒 {timestamp}</span>
                        {f'<span style="font-size: 0.72rem; color: #64748b;">⚡ {latency}</span>' if latency else ''}
                    </div>
                    <div>
                        <span class="source-pill" style="margin: 0; border-color: {badge_color}; color: {badge_color};">
                            {badge_text} ({sim_score})
                        </span>
                    </div>
                </div>
                <div style="font-size: 1.05rem; font-weight: 700; color: #ffffff; margin-bottom: 0.5rem;">
                    ❓ {row.get('Query', '')}
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown(row.get("Answer", ""))

else:
    st.dataframe(filtered_df, use_container_width=True, height=350)


# --- Export Section ---
st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
st.markdown("<h3 style='margin-bottom: 0.5rem;'>📥 Export & Management</h3>", unsafe_allow_html=True)

exp1, exp2, exp3, exp4 = st.columns(4)

# CSV Export
csv_data = df.to_csv(index=False).encode("utf-8")
with exp1:
    st.download_button(
        label="Download CSV Table",
        data=csv_data,
        file_name="crag_session_history.csv",
        mime="text/csv",
        type="primary",
        use_container_width=True
    )

# JSON Export
json_data = json.dumps(history_data, indent=2).encode("utf-8")
with exp2:
    st.download_button(
        label="Download JSON Log",
        data=json_data,
        file_name="crag_session_history.json",
        mime="application/json",
        type="secondary",
        use_container_width=True
    )

# Markdown Report Export
md_report = "# CRAG Document Intelligence - Session Report\n\n"
md_report += f"**Total Queries:** {total_queries}  \n"
md_report += f"**Documents:** {unique_docs}  \n\n---\n\n"
for idx, item in enumerate(history_data):
    md_report += f"## Query {idx + 1}: {item.get('Query')}\n\n"
    md_report += f"- **Timestamp:** {item.get('Timestamp', '')}\n"
    md_report += f"- **Document:** {item.get('Document', '')}\n"
    md_report += f"- **Confidence Level:** {item.get('Confidence', '')} ({item.get('Max_Similarity', '')})\n\n"
    md_report += f"### Answer\n\n{item.get('Answer')}\n\n---\n\n"

with exp3:
    st.download_button(
        label="Download Markdown Report",
        data=md_report.encode("utf-8"),
        file_name="crag_research_report.md",
        mime="text/markdown",
        type="secondary",
        use_container_width=True
    )

with exp4:
    with st.popover("⚠️ Clear History"):
        st.markdown("**Clear all session queries?**")
        st.caption("This action removes all session logs.")
        if st.button("Confirm Clear", type="primary", use_container_width=True):
            st.session_state.history = []
            st.toast("Query history cleared.", icon="🧹")
            st.rerun()