import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from sentence_transformers import SentenceTransformer
import rag_backend as rb


def test_chunk_pages():
    pages = [
        {"page": 1, "text": "This is page 1 content. " * 30},
        {"page": 2, "text": "This is page 2 content. " * 20},
    ]
    chunks = rb.chunk_pages(pages, chunk_size=200, overlap=50)
    assert len(chunks) > 0
    assert chunks[0]["page"] == 1
    assert "id" in chunks[0]
    assert "text" in chunks[0]


def test_indexing_and_crag_retrieval():
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    pages = [
        {"page": 1, "text": "Artificial intelligence and machine learning transform healthcare diagnostic systems."},
        {"page": 2, "text": "Photosynthesis is the process used by plants to convert light energy into chemical energy."},
        {"page": 3, "text": "Quantum computers use qubits which can exist in superposition states."},
    ]
    chunks = rb.chunk_pages(pages, chunk_size=500, overlap=50)
    index = rb.index_chunks(chunks, model)
    assert index is not None

    # Test high confidence query
    result = rb.retrieve_chunks_with_crag(
        "How do plants use light energy?",
        chunks,
        index,
        model,
        top_k=2
    )
    assert len(result["chunks"]) > 0
    assert result["chunks"][0]["page"] == 2
    assert result["confidence_level"] in ["HIGH", "MEDIUM"]
    assert result["max_score"] > 0.4


if __name__ == "__main__":
    test_chunk_pages()
    test_indexing_and_crag_retrieval()
    print("All RAG backend tests passed successfully!")
