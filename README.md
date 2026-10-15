# CRAG - Contextual Retrieval-Augmented Generation

![CRAG Logo](https://github.com/user-attachments/assets/902c1a05-f00e-4f07-b584-6f5311713e71)

CRAG is a powerful document analysis tool that combines Retrieval-Augmented Generation (RAG) with modern web technologies to enable intelligent conversations with your PDF documents. Built with Streamlit and powered by state-of-the-art AI models, CRAG provides a secure, user-friendly interface for document Q&A.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Configuration](#api-configuration)
- [Contributing](#contributing)

---

## Overview

CRAG transforms how you interact with PDF documents by:
- **Secure Authentication:** Firebase-based user authentication system
- **Intelligent PDF Processing:** Extracting and chunking text for optimal retrieval
- **Vector Search:** Using FAISS for fast similarity search across document chunks
- **AI-Powered Q&A:** Leveraging Groq's llama-3.3-70b-versatile model for accurate answers
- **Session Management:** Tracking conversation history with export capabilities
- **Multi-Page Interface:** Clean, intuitive Streamlit web application

---

## Features

### 🔐 **Secure Authentication**
- Firebase Authentication integration
- Email/password registration and login
- Session management and user state persistence

### 📄 **PDF Processing**
- Upload and process PDF documents
- Intelligent text extraction using PDFPlumber
- Automatic text chunking with configurable overlap
- FAISS indexing for efficient similarity search

### 🤖 **AI-Powered Chat**
- Real-time streaming responses
- Context-aware answers based on document content
- Groq API integration with llama-3.3-70b-versatile model
- Retrieval of most relevant document sections

### 📊 **History Management**
- Complete session query history
- CSV export functionality
- Persistent conversation tracking

### 🎨 **Modern UI**
- Responsive Streamlit interface
- Dark theme with custom styling
- Multi-page application structure
- Real-time chat interface

---

## Architecture

```
User Upload PDF → Text Extraction → Chunking → Embedding → FAISS Index
                                                              ↓
User Query → Query Embedding → Similarity Search → Context Retrieval
                                                              ↓
Context + Query → Groq API → llama-3.3-70b-versatile → Streaming Response
```

### **Processing Pipeline:**

1. **Authentication:** Firebase handles user registration and login
2. **PDF Processing:** PDFPlumber extracts text from uploaded documents
3. **Text Chunking:** Content is split into overlapping segments (700 chars with 100 char overlap)
4. **Embedding Generation:** SentenceTransformers creates vector embeddings
5. **Indexing:** FAISS creates searchable index for fast retrieval
6. **Query Processing:** User questions are embedded and matched against document chunks
7. **Answer Generation:** Groq API generates contextual responses using retrieved content

---

## Technology Stack

### **Core Technologies:**
- **Frontend:** Streamlit 1.28.0+
- **Authentication:** Firebase (Pyrebase4)
- **Vector Search:** FAISS (CPU version)
- **Embeddings:** SentenceTransformers (all-MiniLM-L6-v2)
- **LLM API:** Groq (llama-3.3-70b-versatile)
- **PDF Processing:** PDFPlumber
- **Environment Management:** python-dotenv

### **Development Tools:**
- **Testing:** pytest
- **Code Formatting:** black
- **Linting:** flake8
- **Build System:** hatchling

---

## Installation

### Prerequisites
- Python 3.8 or higher
- pip or uv package manager

### Install Dependencies

Using pip:
```bash
pip install -e .
```

Using uv:
```bash
uv pip install -e .
```

Or install from requirements:
```bash
pip install -r requirements.txt
```

---

## Configuration

### 1. Environment Variables

Create a `.env` file in the project root:

```bash
# Firebase Configuration
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_AUTH_DOMAIN=your_project_id.firebaseapp.com
PROJECT_ID=your_project_id
MESSAGING_SENDER_ID=your_sender_id
STORAGE_BUCKET=your_project_id.appspot.com
APP_ID=your_app_id
MEASUREMENT_ID=your_measurement_id
DATABASE_URL=https://your_project_id-default-rtdb.firebaseio.com/

# Groq API Configuration
GROQ_API_KEY=your_groq_api_key
```

### 2. Firebase Setup

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or select existing one
3. Enable Authentication → Sign-in method → Email/Password
4. Get your config from Project Settings → General → Web apps
5. Add the configuration values to your `.env` file

### 3. Groq API Setup

1. Visit [Groq Console](https://console.groq.com/)
2. Create an account and generate an API key
3. Add the API key to your `.env` file

---

## Usage

### 1. Start the Application

```bash
streamlit run main.py
```

### 2. Access the Application

Open your browser and navigate to `http://localhost:8501`

### 3. Using CRAG

1. **Login/Register:** Create an account or login with existing credentials
2. **Upload PDF:** Go to the CRAG App page and upload your PDF document
3. **Process Document:** Click "Process PDF" and wait for indexing to complete
4. **Ask Questions:** Use the chat interface to ask questions about your document
5. **View History:** Check the History page to see all your queries and export as CSV

---

## Project Structure

```
CRAG/
├── main.py                 # Main Streamlit app with authentication
├── rag_backend.py          # Core RAG functionality
├── pyproject.toml          # Project configuration and dependencies
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create this)
├── .gitignore             # Git ignore file
├── README.md              # This file
├── uv.lock                # UV lock file
└── pages/
    ├── crag_app.py        # Main chat interface
    ├── history.py         # Query history page
    └── welcome.html       # Welcome page template
```

### **File Descriptions:**

- **`main.py`:** Entry point with Firebase authentication and home page
- **`rag_backend.py`:** Core RAG logic including PDF processing, indexing, and answer generation
- **`pages/crag_app.py`:** Main application interface for PDF upload and chat
- **`pages/history.py`:** Session history display and CSV export functionality

---

## API Configuration

### **Model Settings:**

- **Embedding Model:** `sentence-transformers/all-MiniLM-L6-v2`
- **LLM Model:** `llama-3.3-70b-versatile` (via Groq)
- **Chunk Size:** 700 characters with 100 character overlap
- **Top-K Retrieval:** 3 most relevant chunks
- **Temperature:** 0.2 for consistent responses

### **Customization Options:**

You can modify these parameters in `rag_backend.py`:
- Chunk size and overlap in `chunk_text()`
- Number of retrieved chunks in `retrieve_chunks()`
- Model temperature and parameters in `generate_answer_stream()`

---

## Development

### **Running Tests:**
```bash
pytest
```

### **Code Formatting:**
```bash
black .
```

### **Linting:**
```bash
flake8
```

### **Building Package:**
```bash
pip install build
python -m build
```

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### **Development Guidelines:**
- Follow PEP 8 style guidelines
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass before submitting PR

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Troubleshooting

### **Common Issues:**

1. **Firebase Configuration Error:**
   - Ensure all Firebase environment variables are set correctly
   - Verify Firebase project has Authentication enabled

2. **Groq API Error:**
   - Check your Groq API key is valid and has sufficient credits
   - Verify internet connection for API calls

3. **PDF Processing Error:**
   - Ensure uploaded file is a valid PDF
   - Check for password-protected or corrupted PDFs

4. **FAISS Index Error:**
   - Verify sufficient memory for large documents
   - Check that sentence-transformers model loads correctly

---

**CRAG empowers you to unlock insights from your documents through intelligent AI-powered conversations. Transform your document analysis workflow today!**
