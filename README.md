# CRAG - Corrective Retrieval-Augmented Generation

![CRAG Architecture](https://github.com/user-attachments/assets/902c1a05-f00e-4f07-b584-6f5311713e71)

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B.svg)](https://streamlit.io/)
[![Groq LPU](https://img.shields.io/badge/Groq-AI%20Inference-orange.svg)](https://groq.com/)
[![FAISS](https://img.shields.io/badge/FAISS-Vector%20Search-blue.svg)](https://github.com/facebookresearch/faiss)

**CRAG** is an intelligent document analysis and Question-Answering platform that integrates **Corrective Retrieval-Augmented Generation (C-RAG)** with high-speed Groq LPU inference. Unlike conventional RAG systems that blindly feed retrieved passages into an LLM, CRAG computes mathematical cosine similarity, evaluates retrieval confidence, flags ambiguous context, and provides exact page-level citations.

---

## ⚡ What Makes CRAG Different?

| Feature | Naive RAG | CRAG Platform |
| :--- | :--- | :--- |
| **Retrieval Evaluation** | ❌ None (blind injection) | ✅ Mathematical Cosine Confidence Gate (High/Medium/Low) |
| **Hallucination Prevention** | ❌ Prone when context is sparse | ✅ Active Corrective Warnings & Fallback Synthesis |
| **Attribution** | ❌ Unclear text excerpts | ✅ Exact Page-Preserved Citations `[Page X]` with Similarity % |
| **Inference Speed** | ⚠️ Slow cloud APIs (3-10s) | ⚡ Sub-second streaming powered by Groq LPUs |
| **Aesthetics & UX** | ⚠️ Basic stock forms | 💎 Obsidian Dark Glassmorphic Design System (1.0 Viewport) |
| **Session Control** | ❌ Temporary / ephemeral | 📊 Interactive Timeline, Analytics KPI Cards, CSV/JSON/MD Export |

---

## 🏗️ System Architecture

```
User Upload (PDF) ──► Page-by-Page Extraction ──► Smart Chunking with Page Tags
                                                           │
                                                           ▼
Question ──► L2-Normalized Embedding ──► FAISS IndexFlatIP (Cosine Similarity)
                                                           │
                                                           ▼
                                            Corrective Evaluation Gate
                                            ┌──────────────┬──────────────┐
                                            ▼              ▼              ▼
                                      High (≥70%)    Medium (45-70%)   Low (<45%)
                                     Direct Synthesis Filtered Context Fallback Warning
                                            │              │              │
                                            └──────────────┼──────────────┘
                                                           ▼
                                                  Groq LLM Streaming
                                                           │
                                                           ▼
                                           Answer + Interactive Citations
```

### Core Pipeline Stages:

1. **Authentication & Identity:** Firebase enterprise authentication with Email/Password plus Instant Guest Explorer access.
2. **Page-Preserving Parser:** Extracts documents per-page using `pdfplumber`, ensuring every chunk retains its true source page metadata.
3. **Exact Cosine Vector Index:** Embeddings generated via `sentence-transformers/all-MiniLM-L6-v2` are L2-normalized and indexed in FAISS Inner-Product space.
4. **Corrective Relevance Gate:** Computes both mean and peak similarity to classify retrieval into `HIGH`, `MEDIUM`, or `LOW` confidence.
5. **Streaming Synthesis:** Passes evaluated context into Groq's low-latency streaming infrastructure with multi-turn memory.

---

## 📁 Repository Structure

```
CRAG/
├── main.py                     # App entrypoint, auth portal & user dashboard
├── rag_backend.py              # Core Corrective RAG engine, FAISS index & Groq streaming
├── ui_styles.py                # Modern obsidian & indigo glassmorphic design system
├── pyproject.toml              # Build metadata and dependencies
├── requirements.txt            # Python dependencies
├── .env.example                # Configuration template
├── .gitignore                  # Comprehensive git exclusions
├── README.md                   # Documentation & setup guide
├── tests/
│   └── test_rag.py             # Unit tests for chunking, indexing & retrieval
└── pages/
    ├── crag_app.py             # Interactive document chat with citations
    └── history.py              # Query analytics, KPI cards & multi-format export
```

---

## 🚀 Quickstart Guide

### 1. Clone the Repository
```bash
git clone https://github.com/SuriyaTheja/CRAG-App.git
cd CRAG-App
```

### 2. Environment Setup
```bash
# Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure API Credentials
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Add your credentials:
```ini
# Groq API Key (Free tier available at https://console.groq.com)
GROQ_API_KEY="gsk_your_groq_api_key_here"

# Firebase Auth Configuration (Optional - Guest Mode is enabled by default)
FIREBASE_API_KEY="your-api-key"
FIREBASE_AUTH_DOMAIN="your-app.firebaseapp.com"
PROJECT_ID="your-project-id"
```

### 4. Run the Platform
```bash
streamlit run main.py
```
Open your browser at `http://localhost:8501`.

---

## 📄 License
This project is licensed under the MIT License.
