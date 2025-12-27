import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
import tempfile
import json
from pathlib import Path

from src.api.main import app

class TestAPI:
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_components(self):
        """Mock all global components"""
        with patch('src.api.main.vector_store_manager') as mock_vsm, \
             patch('src.api.main.rag_engine') as mock_rag, \
             patch('src.api.main.document_processor') as mock_dp, \
             patch('src.api.main.mock_test_engine') as mock_mte:
            
            mock_vsm.get_collection_count.return_value = 100
            yield {
                'vector_store_manager': mock_vsm,
                'rag_engine': mock_rag,
                'document_processor': mock_dp,
                'mock_test_engine': mock_mte
            }
    
    def test_health_check(self, client, mock_components):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["vector_store_count"] == 100
        assert data["version"] == "1.0.0"
    
    def test_query_success(self, client, mock_components):
        """Test successful query"""
        mock_components['rag_engine'].query.return_value = {
            "answer": "Python is a programming language",
            "sources": [
                {
                    "file_name": "python_guide.pdf",
                    "source": "/docs/python_guide.pdf",
                    "chunk_id": 0,
                    "content_preview": "Python is...",
                    "document_type": "learning_material",
                    "company": None,
                    "subject": "Python",
                    "difficulty": "medium",
                    "year": None
                }
            ],
            "confidence": "high",
            "total_sources_found": 1
        }
        
        response = client.post("/query", json={
            "question": "What is Python?",
            "max_docs": 5
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "Python is a programming language"
        assert len(data["sources"]) == 1
        assert data["confidence"] == "high"
    
    def test_query_error(self, client, mock_components):
        """Test query with error"""
        mock_components['rag_engine'].query.side_effect = Exception("Query failed")
        
        response = client.post("/query", json={
            "question": "What is Python?"
        })
        
        assert response.status_code == 500
        assert "Query failed" in response.json()["detail"]
    
    def test_filtered_query_success(self, client, mock_components):
        """Test filtered query"""
        mock_components['vector_store_manager'].similarity_search_with_filters.return_value = [Mock()]
        mock_components['rag_engine'].query_with_docs.return_value = {
            "answer": "Filtered answer",
            "sources": [],
            "confidence": "medium",
            "total_sources_found": 1
        }
        
        response = client.post("/query/filtered", json={
            "question": "Python questions",
            "document_type": "placement_paper",
            "company": "Google",
            "subject": "Python",
            "difficulty": "medium",
            "year": "2023",
            "max_docs": 3
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "Filtered answer"
        
        # Verify filters were applied
        expected_filters = {
            "document_type": "placement_paper",
            "company": "Google",
            "subject": "Python",
            "difficulty": "medium",
            "year": "2023"
        }
        mock_components['vector_store_manager'].similarity_search_with_filters.assert_called_once_with(
            "Python questions", k=3, filters=expected_filters
        )
    
    def test_filtered_query_no_filters(self, client, mock_components):
        """Test filtered query without filters"""
        mock_components['vector_store_manager'].similarity_search.return_value = [Mock()]
        mock_components['rag_engine'].query_with_docs.return_value = {
            "answer": "Answer",
            "sources": [],
            "confidence": "medium",
            "total_sources_found": 1
        }
        
        response = client.post("/query/filtered", json={
            "question": "Test question",
            "max_docs": 5
        })
        
        assert response.status_code == 200
        mock_components['vector_store_manager'].similarity_search.assert_called_once_with(
            "Test question", k=5
        )
    
    def test_get_available_filters(self, client, mock_components):
        """Test getting available filters"""
        mock_components['vector_store_manager'].get_available_filters.return_value = {
            "document_types": ["placement_paper", "mock_test"],
            "companies": ["Google", "Microsoft"],
            "subjects": ["Python", "Java"],
            "difficulties": ["easy", "medium", "hard"],
            "years": ["2022", "2023"]
        }
        
        response = client.get("/filters")
        
        assert response.status_code == 200
        data = response.json()
        assert "Google" in data["companies"]
        assert "Python" in data["subjects"]
        assert "placement_paper" in data["document_types"]
    
    def test_search_documents(self, client, mock_components):
        """Test document search"""
        mock_components['rag_engine'].get_relevant_documents.return_value = [
            {
                "content": "Test content",
                "metadata": {"source": "test.pdf"},
                "relevance_score": 0.8
            }
        ]
        
        response = client.post("/search", json={
            "query": "test search",
            "k": 3
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_results"] == 1
        assert len(data["results"]) == 1
    
    def test_upload_documents_success(self, client, mock_components):
        """Test successful document upload"""
        mock_components['document_processor'].process_document.return_value = [Mock(), Mock()]
        mock_components['vector_store_manager'].add_documents = Mock()
        
        # Create temporary test file
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_file.write(b"Test content")
            tmp_file.flush()
            
            with open(tmp_file.name, "rb") as f:
                response = client.post("/upload", files={"files": ("test.txt", f, "text/plain")})
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["documents_processed"] == 1
        assert data["chunks_created"] == 2
    
    def test_upload_documents_error(self, client, mock_components):
        """Test document upload with error"""
        mock_components['document_processor'].process_document.side_effect = Exception("Processing failed")
        
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_file.write(b"Test content")
            tmp_file.flush()
            
            with open(tmp_file.name, "rb") as f:
                response = client.post("/upload", files={"files": ("test.txt", f, "text/plain")})
        
        assert response.status_code == 500
    
    def test_upload_directory(self, client, mock_components):
        """Test directory upload"""
        response = client.post("/upload-directory", params={"directory_path": "/test/path"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processing"
        assert "background" in data["message"]
    
    def test_reset_vector_store(self, client, mock_components):
        """Test vector store reset"""
        mock_components['vector_store_manager'].reset_collection = Mock()
        
        response = client.delete("/reset")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        mock_components['vector_store_manager'].reset_collection.assert_called_once()
    
    def test_reset_vector_store_error(self, client, mock_components):
        """Test vector store reset with error"""
        mock_components['vector_store_manager'].reset_collection.side_effect = Exception("Reset failed")
        
        response = client.delete("/reset")
        
        assert response.status_code == 500
    
    def test_generate_test(self, client, mock_components):
        """Test mock test generation"""
        mock_components['mock_test_engine'].generate_test.return_value = {
            "test_id": "test123",
            "questions": []
        }
        
        response = client.post("/test/generate", json={
            "subject": "Python",
            "difficulty": "medium",
            "num_questions": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["test_id"] == "test123"
    
    def test_submit_test(self, client, mock_components):
        """Test test submission"""
        mock_components['mock_test_engine'].submit_test.return_value = {
            "test_id": "test123",
            "student_id": "student456",
            "score": 85.0,
            "total_questions": 10,
            "correct_answers": 8,
            "time_taken": 600,
            "subject_scores": {"Python": 85.0},
            "timestamp": "2023-01-01T00:00:00"
        }
        
        response = client.post("/test/submit", json={
            "test_id": "test123",
            "student_id": "student456",
            "answers": [1, 2, 3, 4, 1, 2, 3, 4, 1, 2],
            "time_taken": 600
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["score"] == 85.0
        assert data["correct_answers"] == 8
    
    def test_get_performance(self, client, mock_components):
        """Test getting student performance"""
        mock_components['mock_test_engine'].get_student_performance.return_value = {
            "student_id": "student456",
            "total_tests": 5,
            "average_score": 82.5
        }
        
        response = client.get("/test/performance/student456")
        
        assert response.status_code == 200
        data = response.json()
        assert data["student_id"] == "student456"
        assert data["average_score"] == 82.5
    
    def test_preview_document(self, client, mock_components):
        """Test document preview"""
        mock_doc = Mock()
        mock_doc.metadata = {
            "file_name": "test.pdf",
            "document_type": "learning_material",
            "subject": "Python"
        }
        mock_doc.page_content = "Test content for preview"
        
        mock_components['vector_store_manager'].similarity_search.return_value = [mock_doc]
        
        response = client.get("/document/preview/test_id")
        
        assert response.status_code == 200
        data = response.json()
        assert data["file_name"] == "test.pdf"
        assert data["subject"] == "Python"
        assert "Test content" in data["content_preview"]
    
    def test_preview_document_not_found(self, client, mock_components):
        """Test document preview when not found"""
        mock_components['vector_store_manager'].similarity_search.return_value = []
        
        response = client.get("/document/preview/nonexistent")
        
        assert response.status_code == 404
    
    def test_ai_search_assistant(self, client, mock_components):
        """Test AI search assistant"""
        mock_doc = Mock()
        mock_doc.page_content = "Test content for search"
        mock_doc.metadata = {
            "file_name": "test.pdf",
            "document_type": "learning_material",
            "subject": "Python"
        }
        
        mock_components['vector_store_manager'].similarity_search_with_score.return_value = [
            (mock_doc, 0.85)
        ]
        
        response = client.post("/search/assistant", json={
            "query": "Python programming",
            "k": 5
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "Python programming"
        assert data["total_results"] == 1
        assert data["search_type"] == "keyword_based"
        assert data["results"][0]["relevance_score"] == 0.85
    
    def test_mobile_chat(self, client, mock_components):
        """Test mobile chat interface"""
        mock_components['rag_engine'].query.return_value = {
            "answer": "Mobile response",
            "sources": [
                {"file_name": "doc1.pdf", "document_type": "learning_material"},
                {"file_name": "doc2.pdf", "document_type": "mock_test"},
                {"file_name": "doc3.pdf", "document_type": "placement_paper"}
            ],
            "confidence": "high"
        }
        
        response = client.post("/mobile/chat", json={
            "message": "What is Python?"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "Mobile response"
        assert data["sources_count"] == 3
        assert len(data["sources"]) == 2  # Limited for mobile
        assert data["confidence"] == "high"