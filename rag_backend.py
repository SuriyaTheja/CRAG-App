import os
import faiss
import streamlit as st
import pdfplumber
from groq import Groq
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()

# --- Model and Client Caching ---

@st.cache_resource
def get_groq_client():
    """Returns a cached Groq client."""
    try:
        client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        return client
    except Exception as e:
        st.error(f"Failed to initialize Groq client: {e}")
        return None

@st.cache_resource
def get_sentence_transformer():
    """Returns a cached sentence transformer model."""
    return SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# --- PDF Processing and RAG Logic ---

def extract_text_from_pdf(uploaded_file):
    """Extracts text from an in-memory uploaded PDF file."""
    text = ""
    try:
        # pdfplumber.open() can handle the file-like object from Streamlit
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return ""

def chunk_text(text, chunk_size=700, overlap=100):
    """Chunks text into overlapping segments."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def index_chunks(chunks, model):
    """Creates a FAISS index for text chunks."""
    try:
        embeddings = model.encode(chunks, show_progress_bar=True)
        # Ensure embeddings are float32 for FAISS
        embeddings = embeddings.astype('float32')
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)
        return index
    except Exception as e:
        st.error(f"Error creating FAISS index: {e}")
        return None

def retrieve_chunks(question, chunks, index, model, top_k=3):
    """Retrieves the most relevant chunks for a question."""
    question_embedding = model.encode([question]).astype('float32')
    distances, indices = index.search(question_embedding, top_k)
    return [chunks[i] for i in indices[0]]

def generate_answer_stream(question, chunks):
    """Generates an answer stream using Groq based on context."""
    client = get_groq_client()
    if client is None:
        yield "Error: Groq client not initialized."
        return

    context = "\n\n---\n\n".join(chunks)
    messages = [
        {"role": "system", "content": "You are an expert Q&A assistant. Use the given context to answer the user's question accurately. If the answer is not in the context, state that clearly."},
        {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"}
    ]
    
    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            temperature=0.2,
            top_p=0.1,
            max_tokens=1000,
            stream=True
        )
        
        for chunk in completion:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
                
    except Exception as e:
        yield f"\n\nError calling Groq API: {e}"