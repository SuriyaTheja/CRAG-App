"""
CRAG Chat Application
Interactive Document Analysis with Corrective RAG Evaluation & Live Streaming
"""

import sys
import os
import time
import streamlit as st

# Add workspace root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import rag_backend as rb
import ui_styles

# --- Page Configuration ---
st.set_page_config(
    page_title="CRAG AI | Document Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply global compact 1.0 viewport design system
ui_styles.apply_theme()

# --- Page Authentication Guard ---
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.markdown(
        """
        <div class="crag-hero-container">
            <div class="crag-hero-badge">🔒 SESSION REQUIRED</div>
            <div class="crag-gradient-title" style="font-size: 1.6rem;">Authentication Required</div>
            <p class="crag-subtitle">Please sign in from the main portal to access the CRAG document chat engine.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.page_link("main.py", label="← Return to Login Portal", icon="🔑", use_container_width=True)
    st.stop()

# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "rag_components" not in st.session_state:
    st.session_state.rag_components = None
if "history" not in st.session_state:
    st.session_state.history = []
if "top_k" not in st.session_state:
    st.session_state.top_k = 3
if "confidence_threshold" not in st.session_state:
    st.session_state.confidence_threshold = 0.50
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.2
if "suggested_prompt" not in st.session_state:
    st.session_state.suggested_prompt = None

# --- Sidebar Controls ---
ui_styles.render_sidebar_header()
ui_styles.render_user_profile(st.session_state.user)

st.sidebar.markdown("<p style='font-size: 0.82rem; font-weight: 700; color: #a5b4fc; margin-bottom: 0.35rem;'>📄 Document Upload</p>", unsafe_allow_html=True)
uploaded_file = st.sidebar.file_uploader(
    "Upload Document (PDF)",
    type=["pdf"],
    label_visibility="collapsed",
    help="Upload research papers, technical specs, or reports."
)

if uploaded_file is not None:
    current_doc = st.session_state.rag_components.get("doc_name") if st.session_state.rag_components else None
    btn_label = "⚡ Re-Index Document" if current_doc == uploaded_file.name else "🚀 Process & Index PDF"
    
    if st.sidebar.button(btn_label, type="primary", use_container_width=True):
        progress_bar = st.sidebar.progress(0, text="Initializing SentenceTransformer...")
        
        try:
            model = rb.get_sentence_transformer()
            progress_bar.progress(30, text="Extracting text across pages...")
            
            pages_data = rb.extract_pages_from_pdf(uploaded_file)
            if not pages_data:
                st.sidebar.error("Could not extract readable text from this PDF.")
                st.stop()

            progress_bar.progress(60, text=f"Chunking {len(pages_data)} pages...")
            
            chunks = rb.chunk_pages(pages_data, chunk_size=700, overlap=120)
            if not chunks:
                st.sidebar.error("Document yielded zero text chunks.")
                st.stop()

            progress_bar.progress(85, text=f"Indexing {len(chunks)} chunks in FAISS...")
            
            index = rb.index_chunks(chunks, model)
            if index is None:
                st.sidebar.error("Failed to build FAISS index.")
                st.stop()

            st.session_state.rag_components = {
                "chunks": chunks,
                "index": index,
                "model": model,
                "pages": pages_data,
                "doc_name": uploaded_file.name,
                "pages_count": len(pages_data),
                "total_chars": sum(len(p["text"]) for p in pages_data)
            }
            
            st.session_state.messages = []
            progress_bar.progress(100, text="Ready!")
            time.sleep(0.3)
            progress_bar.empty()
            st.sidebar.success(f"Indexed `{uploaded_file.name}` ({len(pages_data)} pages, {len(chunks)} chunks)")
            st.rerun()

        except Exception as e:
            st.sidebar.error(f"Processing error: {e}")

# Render status card if document is loaded
if st.session_state.rag_components:
    rc = st.session_state.rag_components
    ui_styles.render_status_card(
        doc_name=rc.get("doc_name", "Document"),
        chunk_count=len(rc.get("chunks", []))
    )

    # Document Page Explorer in Sidebar
    if "pages" in rc and rc["pages"]:
        with st.sidebar.expander("📖 Browse Document Pages", expanded=False):
            page_numbers = [p["page"] for p in rc["pages"]]
            selected_page = st.selectbox("Select Page", page_numbers, format_func=lambda p: f"Page {p}")
            page_info = next((p for p in rc["pages"] if p["page"] == selected_page), None)
            if page_info:
                st.caption(f"Words: {page_info.get('word_count', 0)} | Characters: {page_info.get('char_count', 0)}")
                st.text_area("Page Text", value=page_info["text"], height=160, disabled=True)

# Sidebar Retrieval Settings
with st.sidebar.expander("⚙️ Retrieval Settings", expanded=False):
    top_k = st.slider("Top Chunks (k)", min_value=1, max_value=6, value=st.session_state.top_k, step=1)
    st.session_state.top_k = top_k

    temperature = st.slider("Temperature", min_value=0.0, max_value=0.7, value=st.session_state.temperature, step=0.05)
    st.session_state.temperature = temperature

# Action buttons in sidebar
if st.session_state.messages:
    st.sidebar.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
    if st.sidebar.button("🧹 Clear Chat History", type="secondary", use_container_width=True):
        st.session_state.messages = []
        st.toast("Conversation cleared.", icon="✨")
        st.rerun()


# --- Main Chat Header ---
header_col1, header_col2 = st.columns([3, 1])

with header_col1:
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
            <h1 style="margin: 0; font-size: 1.6rem; font-weight: 800;">CRAG Document Chat</h1>
            <span class="crag-hero-badge" style="margin: 0;">CORRECTIVE EVALUATION</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.session_state.rag_components:
        rc = st.session_state.rag_components
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 0.35rem; flex-wrap: wrap; margin-bottom: 0.75rem;">
                <span class="source-pill">📄 <b>{rc['doc_name']}</b></span>
                <span class="source-pill">📑 <b>{rc['pages_count']} Pages</b></span>
                <span class="source-pill">🧩 <b>{len(rc['chunks'])} Vector Chunks</b></span>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            "<p style='color: #94a3b8; font-size: 0.85rem; margin-bottom: 0.75rem;'>Upload a PDF in the sidebar to activate the semantic search and Q&A engine.</p>",
            unsafe_allow_html=True
        )

with header_col2:
    if st.session_state.messages:
        chat_md = "# CRAG Chat Transcript\n\n"
        if st.session_state.rag_components:
            chat_md += f"**Document:** {st.session_state.rag_components['doc_name']}\n\n---\n\n"
        for m in st.session_state.messages:
            role = "### User" if m["role"] == "user" else "### Assistant (CRAG)"
            chat_md += f"{role}\n\n{m['content']}\n\n"

        st.download_button(
            label="📥 Export Chat (.md)",
            data=chat_md,
            file_name="crag_chat_transcript.md",
            mime="text/markdown",
            use_container_width=True
        )

# --- Empty State ---
if not st.session_state.rag_components:
    st.markdown(
        """
        <div class="crag-card" style="text-align: center; padding: 2rem 1.5rem; margin: 1rem 0;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📂</div>
            <div class="crag-card-title" style="font-size: 1.25rem;">No Document Loaded Yet</div>
            <p class="crag-card-desc" style="max-width: 480px; margin: 0.25rem auto 1rem auto;">
                Drag and drop any PDF into the sidebar uploader and click 
                <b style="color: #a5b4fc;">'Process & Index PDF'</b>.
            </p>
            <div style="display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
                <div style="text-align: left; background: rgba(15, 23, 42, 0.7); padding: 0.75rem 1rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06); max-width: 200px;">
                    <div style="font-weight: 700; color: #38bdf8; font-size: 0.85rem;">1. Page Citations</div>
                    <div style="font-size: 0.75rem; color: #94a3b8;">Citations point to actual source page numbers.</div>
                </div>
                <div style="text-align: left; background: rgba(15, 23, 42, 0.7); padding: 0.75rem 1rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06); max-width: 200px;">
                    <div style="font-weight: 700; color: #818cf8; font-size: 0.85rem;">2. FAISS Cosine Index</div>
                    <div style="font-size: 0.75rem; color: #94a3b8;">Fast semantic vector embeddings.</div>
                </div>
                <div style="text-align: left; background: rgba(15, 23, 42, 0.7); padding: 0.75rem 1rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06); max-width: 200px;">
                    <div style="font-weight: 700; color: #10b981; font-size: 0.85rem;">3. Corrective Check</div>
                    <div style="font-size: 0.75rem; color: #94a3b8;">Relevance evaluated to reduce hallucinations.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    # Quick Suggested Questions Chips
    if not st.session_state.messages:
        st.markdown("<p style='font-size: 0.8rem; font-weight: 600; color: #94a3b8; margin-bottom: 0.35rem;'>💡 Suggested Quick Questions:</p>", unsafe_allow_html=True)
        q_col1, q_col2, q_col3, q_col4 = st.columns(4)

        if q_col1.button("📄 Summary", use_container_width=True):
            st.session_state.suggested_prompt = "Provide a comprehensive summary of this document, highlighting its core objectives and findings."
        if q_col2.button("🎯 Key Takeaways", use_container_width=True):
            st.session_state.suggested_prompt = "What are the most critical takeaways and conclusions presented in this document?"
        if q_col3.button("⚠️ Limitations", use_container_width=True):
            st.session_state.suggested_prompt = "What challenges, risks, limitations, or caveats are highlighted in this text?"
        if q_col4.button("📋 Action Items", use_container_width=True):
            st.session_state.suggested_prompt = "Extract all recommended action items and practical implications from the document."


# --- Display Chat Messages ---
for msg_idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        if msg.get("role") == "assistant" and "retrieval_data" in msg:
            rd = msg["retrieval_data"]
            conf_level = rd.get("confidence_level", "HIGH")
            max_score = rd.get("max_score", 0.0)
            retrieval_ms = msg.get("retrieval_ms", 0)
            generation_sec = msg.get("generation_sec", 0)
            orig_query = msg.get("user_query", "")
            
            # Confidence styling
            if conf_level == "HIGH":
                meter_color = "#10b981"
                conf_text = f"🟢 High Confidence ({max_score:.0%})"
            elif conf_level == "MEDIUM":
                meter_color = "#f59e0b"
                conf_text = f"🟡 Moderate Confidence ({max_score:.0%})"
            else:
                meter_color = "#ef4444"
                conf_text = f"🔴 Low Relevance ({max_score:.0%})"

            # Execution telemetry badge row
            metrics_html = f"""
            <div style="display: flex; gap: 0.6rem; align-items: center; font-size: 0.72rem; color: #64748b; margin-top: 0.4rem; margin-bottom: 0.4rem; flex-wrap: wrap;">
                <span>⚡ <b>{retrieval_ms:.0f}ms</b> vector search</span>
                <span>•</span>
                <span>⏱️ <b>{generation_sec:.2f}s</b> generation</span>
                <span>•</span>
                <span>🔍 <b>{len(rd.get('chunks', []))}</b> passages evaluated</span>
                <span>•</span>
                <span style="color: {meter_color}; font-weight: 600;">{conf_text}</span>
            </div>
            """
            st.markdown(metrics_html, unsafe_allow_html=True)

            with st.expander(f"🔍 Evaluated Retrieval Sources & Key Excerpts", expanded=False):
                for idx, chunk in enumerate(rd.get("chunks", [])):
                    page_badge = f"Page {chunk.get('page', '?')}"
                    sim_pct = f"{chunk.get('score', 0):.1%}"
                    # Highlight matched keywords in chunk text
                    chunk_text = chunk.get("text", "")
                    highlighted = rb.highlight_keywords(chunk_text, orig_query)

                    st.markdown(
                        f"""
                        <div style="margin-bottom: 0.5rem;">
                            <div style="display: flex; gap: 0.5rem; align-items: center;">
                                <span class="source-pill" style="margin: 0;">📑 Source {idx + 1} &bull; {page_badge}</span>
                                <span style="font-size: 0.72rem; color: #94a3b8;">Cosine Similarity: <b>{sim_pct}</b></span>
                            </div>
                            <div class="source-content-box">
                                {highlighted}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


# --- Handle Input ---
prompt = st.chat_input("Ask any question regarding the active document...")

if st.session_state.suggested_prompt:
    prompt = st.session_state.suggested_prompt
    st.session_state.suggested_prompt = None

if prompt:
    if st.session_state.rag_components is None:
        st.warning("Please upload and index a PDF first using the sidebar.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        rag_data = st.session_state.rag_components
        
        # Measure vector search latency
        t_start_retrieval = time.perf_counter()
        with st.spinner("Retrieving and evaluating relevance..."):
            retrieval_data = rb.retrieve_chunks_with_crag(
                question=prompt,
                chunks=rag_data["chunks"],
                index=rag_data["index"],
                model=rag_data["model"],
                top_k=st.session_state.top_k,
                confidence_threshold=st.session_state.confidence_threshold
            )
        retrieval_ms = (time.perf_counter() - t_start_retrieval) * 1000.0

        # Measure generation duration
        t_start_gen = time.perf_counter()
        response_stream = rb.generate_crag_answer_stream(
            question=prompt,
            retrieval_data=retrieval_data,
            temperature=st.session_state.temperature,
            chat_history=st.session_state.messages[:-1]
        )

        full_response = st.write_stream(response_stream)
        generation_sec = time.perf_counter() - t_start_gen

        conf_level = retrieval_data.get("confidence_level", "HIGH")
        max_score = retrieval_data.get("max_score", 0.0)
        
        if conf_level == "HIGH":
            meter_color = "#10b981"
            conf_text = f"🟢 High Confidence ({max_score:.0%})"
        elif conf_level == "MEDIUM":
            meter_color = "#f59e0b"
            conf_text = f"🟡 Moderate Confidence ({max_score:.0%})"
        else:
            meter_color = "#ef4444"
            conf_text = f"🔴 Low Relevance ({max_score:.0%})"

        # Execution telemetry badge row
        metrics_html = f"""
        <div style="display: flex; gap: 0.6rem; align-items: center; font-size: 0.72rem; color: #64748b; margin-top: 0.4rem; margin-bottom: 0.4rem; flex-wrap: wrap;">
            <span>⚡ <b>{retrieval_ms:.0f}ms</b> vector search</span>
            <span>•</span>
            <span>⏱️ <b>{generation_sec:.2f}s</b> generation</span>
            <span>•</span>
            <span>🔍 <b>{len(retrieval_data.get('chunks', []))}</b> passages evaluated</span>
            <span>•</span>
            <span style="color: {meter_color}; font-weight: 600;">{conf_text}</span>
        </div>
        """
        st.markdown(metrics_html, unsafe_allow_html=True)

        with st.expander(f"🔍 Evaluated Retrieval Sources & Key Excerpts", expanded=False):
            for idx, chunk in enumerate(retrieval_data.get("chunks", [])):
                page_badge = f"Page {chunk.get('page', '?')}"
                sim_pct = f"{chunk.get('score', 0):.1%}"
                chunk_text = chunk.get("text", "")
                highlighted = rb.highlight_keywords(chunk_text, prompt)

                st.markdown(
                    f"""
                    <div style="margin-bottom: 0.5rem;">
                        <div style="display: flex; gap: 0.5rem; align-items: center;">
                            <span class="source-pill" style="margin: 0;">📑 Source {idx + 1} &bull; {page_badge}</span>
                            <span style="font-size: 0.72rem; color: #94a3b8;">Cosine Similarity: <b>{sim_pct}</b></span>
                        </div>
                        <div class="source-content-box">
                            {highlighted}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response,
        "retrieval_data": retrieval_data,
        "retrieval_ms": retrieval_ms,
        "generation_sec": generation_sec,
        "user_query": prompt
    })

    st.session_state.history.append({
        "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "Document": rag_data.get("doc_name", "Document"),
        "Query": prompt,
        "Answer": full_response,
        "Model": rb.GROQ_MODEL,
        "Confidence": retrieval_data.get("confidence_level", "HIGH"),
        "Max_Similarity": f"{retrieval_data.get('max_score', 0):.1%}",
        "Chunks_Used": len(retrieval_data.get("chunks", [])),
        "Latency_ms": f"{retrieval_ms:.0f}ms"
    })