"""
CRAG Backend: Contextual & Corrective Retrieval-Augmented Generation Engine
Handles page-aware PDF text extraction, SentenceTransformer vector embeddings,
FAISS cosine-similarity index, keyword term highlighting, and confidence-evaluated corrective generation with Groq.
"""

import os
import re
from typing import Dict, List, Any, Generator
import faiss
import numpy as np
import pdfplumber
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv(dotenv_path="./.env")

# Fixed model as configured for current Groq access
GROQ_MODEL = "openai/gpt-oss-120b"


# --- Model and Client Caching ---

@st.cache_resource(show_spinner=False)
def get_groq_client() -> Groq | None:
    """Returns a cached Groq client using environment variable GROQ_API_KEY."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    try:
        return Groq(api_key=api_key.strip())
    except Exception as e:
        st.error(f"Failed to initialize Groq client: {e}")
        return None


@st.cache_resource(show_spinner=False)
def get_sentence_transformer() -> SentenceTransformer:
    """Returns a cached SentenceTransformer model."""
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


# --- Page-Aware PDF Processing & Chunking ---

def extract_pages_from_pdf(uploaded_file) -> List[Dict[str, Any]]:
    """
    Extracts text page-by-page from an in-memory uploaded PDF file.
    Returns list of dicts: [{"page": 1, "text": "...", "word_count": N}].
    """
    pages_data = []
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            for idx, page in enumerate(pdf.pages):
                page_text = page.extract_text() or ""
                cleaned_text = re.sub(r"\n{3,}", "\n\n", page_text).strip()
                if cleaned_text:
                    pages_data.append({
                        "page": idx + 1,
                        "text": cleaned_text,
                        "word_count": len(cleaned_text.split()),
                        "char_count": len(cleaned_text)
                    })
        return pages_data
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return []


def chunk_pages(
    pages_data: List[Dict[str, Any]], 
    chunk_size: int = 700, 
    overlap: int = 120
) -> List[Dict[str, Any]]:
    """
    Chunks document text preserving source page numbers and applying overlap.
    """
    chunks = []
    chunk_id = 1

    for page_info in pages_data:
        page_num = page_info["page"]
        text = page_info["text"]
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk_content = text[start:end].strip()

            if chunk_content:
                chunks.append({
                    "id": chunk_id,
                    "page": page_num,
                    "text": chunk_content,
                    "char_count": len(chunk_content)
                })
                chunk_id += 1

            start += chunk_size - overlap

    return chunks


# Backward-compatible text extractor and chunker
def extract_text_from_pdf(uploaded_file):
    pages = extract_pages_from_pdf(uploaded_file)
    return "\n\n".join(p["text"] for p in pages)


def chunk_text(text, chunk_size=700, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


# --- Keyword Highlighting Utility ---

def highlight_keywords(text: str, query: str) -> str:
    """
    Highlights significant query terms within the source excerpt using soft HTML mark tags.
    """
    stopwords = {
        "what", "when", "where", "which", "who", "whom", "this", "that", "these", "those",
        "from", "with", "about", "into", "through", "during", "before", "after", "above",
        "below", "to", "in", "for", "on", "by", "at", "the", "and", "a", "an", "is",
        "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does",
        "did", "can", "could", "should", "would", "how", "why", "tell", "show", "give"
    }
    words = set(re.findall(r"\b[a-zA-Z]{3,}\b", query.lower()))
    keywords = [w for w in words if w not in stopwords]
    if not keywords:
        return text

    pattern = re.compile(rf"\b({'|'.join(re.escape(k) for k in keywords)})\b", re.IGNORECASE)
    return pattern.sub(
        r'<mark style="background: rgba(99, 102, 241, 0.35); color: #ffffff; border-radius: 3px; padding: 1px 4px;">\1</mark>',
        text
    )


# --- FAISS Cosine Similarity Indexing ---

def index_chunks(chunks: List[Any], model: SentenceTransformer):
    """
    Creates an exact cosine-similarity FAISS index.
    L2 normalization of embeddings allows Inner Product (IndexFlatIP) to produce true cosine similarity.
    """
    if not chunks:
        return None

    try:
        if isinstance(chunks[0], dict):
            chunk_texts = [c["text"] for c in chunks]
        else:
            chunk_texts = [str(c) for c in chunks]

        embeddings = model.encode(chunk_texts, show_progress_bar=False)
        embeddings = np.array(embeddings, dtype="float32")

        faiss.normalize_L2(embeddings)

        dim = embeddings.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(embeddings)
        return index
    except Exception as e:
        st.error(f"Error creating FAISS vector index: {e}")
        return None


# --- Corrective Retrieval & Confidence Scoring ---

def retrieve_chunks_with_crag(
    question: str,
    chunks: List[Any],
    index: faiss.Index,
    model: SentenceTransformer,
    top_k: int = 3,
    confidence_threshold: float = 0.50
) -> Dict[str, Any]:
    """
    Performs vector similarity search and evaluates retrieval confidence:
    - High Match: Reliable semantic match in document.
    - Medium Match: Partial or ambiguous coverage.
    - Low Match: Little to no direct match; triggers corrective answer warnings.
    """
    top_k = min(top_k, len(chunks))
    q_emb = model.encode([question], show_progress_bar=False)
    q_emb = np.array(q_emb, dtype="float32")
    faiss.normalize_L2(q_emb)

    similarities, indices = index.search(q_emb, top_k)

    retrieved_items = []
    scores = []

    for sim, idx in zip(similarities[0], indices[0]):
        if 0 <= idx < len(chunks):
            item = chunks[idx]
            if isinstance(item, dict):
                chunk = item.copy()
            else:
                chunk = {"text": str(item), "page": "?"}

            norm_score = max(0.0, min(1.0, float(sim)))
            chunk["score"] = norm_score
            retrieved_items.append(chunk)
            scores.append(norm_score)

    avg_score = float(np.mean(scores)) if scores else 0.0
    max_score = float(np.max(scores)) if scores else 0.0

    # CRAG confidence categorization
    if max_score >= 0.65 or avg_score >= 0.58:
        confidence_level = "HIGH"
        confidence_label = "Strong Match"
        needs_correction = False
    elif max_score >= confidence_threshold or avg_score >= 0.42:
        confidence_level = "MEDIUM"
        confidence_label = "Partial Match"
        needs_correction = True
    else:
        confidence_level = "LOW"
        confidence_label = "Low Match (Fallback)"
        needs_correction = True

    return {
        "chunks": retrieved_items,
        "avg_score": avg_score,
        "max_score": max_score,
        "confidence_level": confidence_level,
        "confidence_label": confidence_label,
        "needs_correction": needs_correction
    }


def retrieve_chunks(question, chunks, index, model, top_k=3):
    res = retrieve_chunks_with_crag(question, chunks, index, model, top_k)
    return [c["text"] for c in res["chunks"]]


# --- Answer Generation Stream using Groq ---

def generate_crag_answer_stream(
    question: str,
    retrieval_data: Dict[str, Any],
    temperature: float = 0.2,
    max_tokens: int = 1500,
    chat_history: List[Dict[str, str]] | None = None
) -> Generator[str, None, None]:
    """
    Streams answers from Groq model (openai/gpt-oss-120b) with corrective grounding.
    """
    client = get_groq_client()
    if client is None:
        yield "⚠️ **Error:** Groq client is not initialized. Please verify your `GROQ_API_KEY`."
        return

    chunks = retrieval_data.get("chunks", [])
    confidence_level = retrieval_data.get("confidence_level", "HIGH")

    # Format context with page markers
    context_blocks = []
    for c in chunks:
        page_info = f"[Page {c.get('page', '?')}]" if isinstance(c, dict) and "page" in c else ""
        text = c["text"] if isinstance(c, dict) else str(c)
        score_info = f"(Relevance: {c.get('score', 0):.0%})" if isinstance(c, dict) and "score" in c else ""
        context_blocks.append(f"--- Document Source {page_info} {score_info} ---\n{text}")

    context = "\n\n".join(context_blocks)

    system_prompt = (
        "You are CRAG (Corrective Retrieval-Augmented Generation), an expert document Q&A assistant.\n"
        "Guidelines:\n"
        "1. Answer the question accurately using ONLY the provided document context.\n"
        "2. When stating facts from the context, include page citations like [Page X].\n"
        "3. If the context does not contain enough information to answer, state this clearly rather than guessing.\n"
        f"4. The retrieval confidence for this query is {confidence_level}. "
    )
    if confidence_level == "LOW":
        system_prompt += (
            "Because retrieval confidence is low, warn the user that the document has limited or no direct information "
            "on this topic, and only provide what is strictly supported."
        )

    messages = [{"role": "system", "content": system_prompt}]

    if chat_history:
        for turn in chat_history[-4:]:
            if turn.get("role") in ["user", "assistant"]:
                messages.append({"role": turn["role"], "content": turn["content"]})

    messages.append({
        "role": "user",
        "content": f"Context:\n{context}\n\nQuestion: {question}"
    })

    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=temperature,
            top_p=0.1,
            max_tokens=max_tokens,
            stream=True
        )

        for chunk in completion:
            if chunk.choices and chunk.choices[0].delta:
                delta = chunk.choices[0].delta
                if hasattr(delta, "content") and delta.content is not None:
                    yield delta.content

    except Exception as e:
        yield f"\n\n⚠️ **Error contacting Groq API:** `{e}`"


def generate_answer_stream(question, chunks):
    retrieval_data = {
        "chunks": [{"text": c if isinstance(c, str) else c["text"], "page": "?"} for c in chunks],
        "confidence_level": "HIGH"
    }
    return generate_crag_answer_stream(question, retrieval_data)