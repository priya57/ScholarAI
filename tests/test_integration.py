import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, Mock
import os

from src.core.document_processor import DocumentProcessor
from src.core.vector_store import VectorStoreManager
from src.core.rag_engine import RAGEngine

class TestIntegration:
    """Integration tests for the complete RAG pipeline"""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary directory with test documents"""
        temp_dir = tempfile.mkdtemp()
        
        # Create test documents
        docs_dir = Path(temp_dir) / "documents"
        docs_dir.mkdir()
        
        # Create a placement paper
        placement_dir = docs_dir / "Cocubes"
        placement_dir.mkdir()
        (placement_dir / "cocubes_quant_2023.txt").write_text(
            "Quantitative Aptitude Questions:\n"
            "1. What is 2 + 2?\n"
            "Answer: 4\n"
            "2. Calculate the area of a circle with radius 5.\n"
            "Answer: 78.54 square units"
        )
        
        # Create a learning material
        (docs_dir / "python_basics.txt").write_text(
            "Python Programming Basics:\n"
            "Python is a high-level programming language.\n"
            "It is used for web development, data science, and automation.\n"
            "Variables in Python are dynamically typed."
        )
        
        # Create a mock test
        (docs_dir / "mock_test_python.txt").write_text(
            "Python Mock Test:\n"
            "1. What is Python?\n"
            "a) A snake b) A programming language c) A framework\n"
            "Answer: b\n"
            "2. Which keyword is used to define a function?\n"
            "a) func b) def c) function\n"
            "Answer: b"
        )
        
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @patch('src.core.vector_store.OpenAIEmbeddings')
    @patch('src.core.vector_store.chromadb.PersistentClient')
    @patch('src.core.vector_store.Chroma')
    def test_document_processing_pipeline(self, mock_chroma, mock_client, mock_embeddings, temp_data_dir):
        """Test complete document processing pipeline"""
        # Initialize components
        processor = DocumentProcessor(chunk_size=100, chunk_overlap=20)
        
        # Process documents
        docs_dir = Path(temp_data_dir) / "documents"
        documents = processor.process_directory(str(docs_dir))
        
        # Verify documents were processed
        assert len(documents) > 0
        
        # Check metadata extraction
        placement_docs = [d for d in documents if d.metadata.get("document_type") == "placement_paper"]
        learning_docs = [d for d in documents if d.metadata.get("document_type") == "learning_material"]
        mock_test_docs = [d for d in documents if d.metadata.get("document_type") == "mock_test"]
        
        assert len(placement_docs) > 0
        assert len(learning_docs) > 0
        assert len(mock_test_docs) > 0
        
        # Verify placement paper metadata
        cocubes_doc = next((d for d in placement_docs if "cocubes" in d.metadata.get("source", "").lower()), None)
        assert cocubes_doc is not None
        assert cocubes_doc.metadata.get("company") == "Cocubes"
        assert cocubes_doc.metadata.get("subject") == "Quantitative Aptitude"
        assert cocubes_doc.metadata.get("year") == "2023"
    
    @patch('src.core.rag_engine.ChatOpenAI')
    @patch('src.core.rag_engine.RetrievalQA')
    @patch('src.core.vector_store.OpenAIEmbeddings')
    @patch('src.core.vector_store.chromadb.PersistentClient')
    @patch('src.core.vector_store.Chroma')
    def test_rag_pipeline_integration(self, mock_chroma, mock_client, mock_embeddings, 
                                    mock_retrieval_qa, mock_chat_openai, temp_data_dir):
        """Test complete RAG pipeline integration"""
        # Setup mocks
        mock_vector_store = Mock()
        mock_chroma.return_value = mock_vector_store
        
        mock_llm = Mock()
        mock_chat_openai.return_value = mock_llm
        
        mock_qa_chain = Mock()
        mock_retrieval_qa.from_chain_type.return_value = mock_qa_chain
        
        # Initialize components
        processor = DocumentProcessor(chunk_size=100, chunk_overlap=20)
        vector_store_manager = VectorStoreManager(
            persist_directory=str(Path(temp_data_dir) / "chroma"),
            collection_name="test_collection",
            openai_api_key="test-key"
        )
        rag_engine = RAGEngine(
            vector_store_manager=vector_store_manager,
            openai_api_key="test-key"
        )
        
        # Process and add documents
        docs_dir = Path(temp_data_dir) / "documents"
        documents = processor.process_directory(str(docs_dir))
        vector_store_manager.add_documents(documents)
        
        # Mock query response
        mock_qa_chain.return_value = {
            "result": "Python is a programming language used for various applications.",
            "source_documents": documents[:2]
        }
        
        # Test query
        result = rag_engine.query("What is Python?")
        
        assert "Python is a programming language" in result["answer"]
        assert len(result["sources"]) == 2
        assert result["total_sources_found"] == 2
    
    @patch('src.core.vector_store.OpenAIEmbeddings')
    @patch('src.core.vector_store.chromadb.PersistentClient')
    @patch('src.core.vector_store.Chroma')
    def test_filtering_integration(self, mock_chroma, mock_client, mock_embeddings, temp_data_dir):
        """Test document filtering integration"""
        # Setup mocks
        mock_vector_store = Mock()
        mock_chroma.return_value = mock_vector_store
        
        # Initialize components
        processor = DocumentProcessor(chunk_size=100, chunk_overlap=20)
        vector_store_manager = VectorStoreManager(
            persist_directory=str(Path(temp_data_dir) / "chroma"),
            collection_name="test_collection",
            openai_api_key="test-key"
        )
        
        # Process documents
        docs_dir = Path(temp_data_dir) / "documents"
        documents = processor.process_directory(str(docs_dir))
        
        # Mock filtered search
        placement_docs = [d for d in documents if d.metadata.get("document_type") == "placement_paper"]
        mock_vector_store.similarity_search.return_value = placement_docs
        
        # Test filtering
        result = vector_store_manager.filter_by_document_type("math questions", "placement_paper")
        
        mock_vector_store.similarity_search.assert_called_with(
            "math questions", k=5, filter={"document_type": "placement_paper"}
        )
    
    def test_error_handling_integration(self, temp_data_dir):
        """Test error handling in integration scenarios"""
        processor = DocumentProcessor()
        
        # Test with non-existent directory
        documents = processor.process_directory("/nonexistent/path")
        assert documents == []
        
        # Test with directory containing unsupported files
        unsupported_dir = Path(temp_data_dir) / "unsupported"
        unsupported_dir.mkdir()
        (unsupported_dir / "test.xyz").write_text("unsupported content")
        
        documents = processor.process_directory(str(unsupported_dir))
        assert documents == []
    
    @patch('src.core.vector_store.OpenAIEmbeddings')
    @patch('src.core.vector_store.chromadb.PersistentClient')
    @patch('src.core.vector_store.Chroma')
    def test_metadata_consistency_integration(self, mock_chroma, mock_client, mock_embeddings, temp_data_dir):
        """Test metadata consistency across the pipeline"""
        processor = DocumentProcessor(chunk_size=50, chunk_overlap=10)
        
        # Process documents
        docs_dir = Path(temp_data_dir) / "documents"
        documents = processor.process_directory(str(docs_dir))
        
        # Check metadata consistency
        for doc in documents:
            # All documents should have required metadata
            assert "source" in doc.metadata
            assert "file_name" in doc.metadata
            assert "file_type" in doc.metadata
            assert "document_type" in doc.metadata
            assert "chunk_id" in doc.metadata
            assert "total_chunks" in doc.metadata
            assert "difficulty" in doc.metadata
            
            # Chunk IDs should be valid
            assert isinstance(doc.metadata["chunk_id"], int)
            assert doc.metadata["chunk_id"] >= 0
            assert doc.metadata["total_chunks"] > 0
            assert doc.metadata["chunk_id"] < doc.metadata["total_chunks"]
    
    def test_chunking_consistency_integration(self, temp_data_dir):
        """Test document chunking consistency"""
        processor = DocumentProcessor(chunk_size=50, chunk_overlap=10)
        
        # Create a longer document
        long_doc_path = Path(temp_data_dir) / "long_document.txt"
        long_content = "This is a test document. " * 20  # Create content that will be chunked
        long_doc_path.write_text(long_content)
        
        documents = processor.process_document(str(long_doc_path))
        
        # Verify chunking
        assert len(documents) > 1  # Should be chunked
        
        # Check chunk sequence
        chunk_ids = [doc.metadata["chunk_id"] for doc in documents]
        assert chunk_ids == list(range(len(documents)))
        
        # Check total_chunks consistency
        total_chunks = documents[0].metadata["total_chunks"]
        assert all(doc.metadata["total_chunks"] == total_chunks for doc in documents)
        assert total_chunks == len(documents)
    
    @patch('src.core.vector_store.OpenAIEmbeddings')
    @patch('src.core.vector_store.chromadb.PersistentClient')
    @patch('src.core.vector_store.Chroma')
    def test_company_detection_integration(self, mock_chroma, mock_client, mock_embeddings, temp_data_dir):
        """Test company detection across different folder structures"""
        processor = DocumentProcessor()
        
        # Create company-specific folders
        companies = ["Google", "Microsoft", "Amazon"]
        for company in companies:
            company_dir = Path(temp_data_dir) / company.lower()
            company_dir.mkdir()
            (company_dir / f"{company.lower()}_questions.txt").write_text(
                f"{company} interview questions and answers."
            )
        
        documents = processor.process_directory(temp_data_dir)
        
        # Verify company detection
        for company in companies:
            company_docs = [d for d in documents if d.metadata.get("company") == company]
            assert len(company_docs) > 0, f"No documents found for {company}"
    
    def test_subject_detection_integration(self, temp_data_dir):
        """Test subject detection from filenames"""
        processor = DocumentProcessor()
        
        # Create subject-specific files
        subjects = {
            "python_advanced.txt": "Python",
            "java_basics.txt": "Java", 
            "javascript_tutorial.txt": "JavaScript",
            "sql_queries.txt": "SQL",
            "algorithms_guide.txt": "Algorithms"
        }
        
        for filename, expected_subject in subjects.items():
            file_path = Path(temp_data_dir) / filename
            file_path.write_text(f"Content about {expected_subject}")
        
        documents = processor.process_directory(temp_data_dir)
        
        # Verify subject detection
        for filename, expected_subject in subjects.items():
            subject_docs = [d for d in documents 
                          if expected_subject in d.metadata.get("subject", "") 
                          and filename in d.metadata.get("source", "")]
            assert len(subject_docs) > 0, f"Subject {expected_subject} not detected in {filename}"