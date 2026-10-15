import sys
import os

# Add the parent directory (ragapp) to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now this import will work
import rag_backend as rb  # Import our backend logic
import streamlit as st
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="CRAG App",
    page_icon="🤖",
    layout="wide"
)

# --- Background Image and Styling (Same as Home) ---
def set_styles():
    st.markdown(f"""
    <style>
    .stApp {{
        background-color: black;
        background-size: cover;
        background-attachment: fixed;
    }}
    /* Style for sidebar content */
    [data-testid="stSidebarContent"] {{
        background-color: black;
        border-radius: 10px;
        margin: 10px;
        border: 1px solid rgb(50, 100, 200);
    }}
    /* Chat message containers */
    [data-testid="chat-message-container"] {{
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 12px 0 rgba(31, 38, 135, 0.1);
    }}
    /* Main chat input box */
    [data-testid="stChatInput"] {{
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        padding: 1rem;
    }}
    </style>
    """, unsafe_allow_html=True)

set_styles()

# --- Page Protection ---
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Please log in from the `1_Home` page to use the app.")
    st.stop()

# --- Initialize Session State Variables ---
# For chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
# For RAG components (index, chunks, etc.)
if "rag_components" not in st.session_state:
    st.session_state.rag_components = None
# For session history (for the History page)
if "history" not in st.session_state:
    st.session_state.history = []

# --- Sidebar for PDF Upload and Processing ---
with st.sidebar:
    st.title("📄 PDF Processing")
    uploaded_file = st.file_uploader("Upload your PDF", type="pdf")
    
    if st.button("Process PDF", type="primary"):
        if uploaded_file is not None:
            with st.spinner("Processing PDF... This may take a moment."):
                try:
                    # 1. Get the model
                    model = rb.get_sentence_transformer()
                    
                    # 2. Extract text
                    text = rb.extract_text_from_pdf(uploaded_file)
                    if not text:
                        st.error("No text could be extracted from the PDF.")
                        st.stop()
                        
                    # 3. Chunk text
                    chunks = rb.chunk_text(text)
                    
                    # 4. Index chunks
                    index = rb.index_chunks(chunks, model)
                    if index is None:
                        st.error("Failed to create document index.")
                        st.stop()
                    
                    # 5. Store components in session state
                    st.session_state.rag_components = {
                        "chunks": chunks,
                        "index": index,
                        "model": model,
                        "doc_name": uploaded_file.name
                    }
                    
                    # Clear chat history for the new document
                    st.session_state.messages = []
                    
                    st.success(f"Successfully processed `{uploaded_file.name}`! You can now ask questions.")
                except Exception as e:
                    st.error(f"An error occurred during processing: {e}")
        else:
            st.warning("Please upload a PDF file first.")

# --- Main Chat Interface ---
st.title("🤖 CRAG Chat")

if st.session_state.rag_components:
    st.info(f"Chatting with: `{st.session_state.rag_components['doc_name']}`")
else:
    st.info("Please upload and process a PDF in the sidebar to begin.")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle new user input
if prompt := st.chat_input("Ask a question about your document..."):
    if st.session_state.rag_components is None:
        st.warning("Please process a PDF first.")
        st.stop()

    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate and stream assistant's response
    with st.chat_message("assistant"):
        rag_data = st.session_state.rag_components
        
        # 1. Retrieve
        relevant_chunks = rb.retrieve_chunks(
            prompt, rag_data["chunks"], rag_data["index"], rag_data["model"]
        )
        
        # 2. Generate
        response_stream = rb.generate_answer_stream(prompt, relevant_chunks)
        
        # st.write_stream handles the streaming output dynamically
        full_response = st.write_stream(response_stream)

    # Add assistant's full response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    # Add to persistent history for the History page
    st.session_state.history.append({"Query": prompt, "Answer": full_response})