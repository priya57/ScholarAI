import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import os

from src.core.document_processor import DocumentProcessor
from src.core.vector_store import VectorStoreManager
from src.core.rag_engine import RAGEngine
from src.core.config import settings

@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_pdf_path(temp_dir):
    """Create a sample PDF file for testing"""
    pdf_path = Path(temp_dir) / "test_document.pdf"
    # Create a minimal PDF content for testing
    pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 44 >>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(Test content) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000206 00000 n \ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n299\n%%EOF"
    with open(pdf_path, 'wb') as f:
        f.write(pdf_content)
    return str(pdf_path)

@pytest.fixture
def sample_txt_path(temp_dir):
    """Create a sample text file for testing"""
    txt_path = Path(temp_dir) / "test_document.txt"
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write("This is a test document with sample content for testing purposes.")
    return str(txt_path)

@pytest.fixture
def mock_openai_api_key():
    """Mock OpenAI API key"""
    return "test-api-key"

@pytest.fixture
def document_processor():
    """Create DocumentProcessor instance"""
    return DocumentProcessor(chunk_size=100, chunk_overlap=20)

@pytest.fixture
def mock_vector_store_manager(temp_dir, mock_openai_api_key):
    """Create mock VectorStoreManager"""
    with patch('src.core.vector_store.OpenAIEmbeddings'):
        with patch('src.core.vector_store.chromadb.PersistentClient'):
            with patch('src.core.vector_store.Chroma'):
                return VectorStoreManager(
                    persist_directory=temp_dir,
                    collection_name="test_collection",
                    openai_api_key=mock_openai_api_key
                )

@pytest.fixture
def mock_rag_engine(mock_vector_store_manager, mock_openai_api_key):
    """Create mock RAGEngine"""
    with patch('src.core.rag_engine.ChatOpenAI'):
        with patch('src.core.rag_engine.RetrievalQA'):
            return RAGEngine(
                vector_store_manager=mock_vector_store_manager,
                openai_api_key=mock_openai_api_key
            )