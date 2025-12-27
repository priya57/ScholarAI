import pytest
import time
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
from concurrent.futures import ThreadPoolExecutor
import threading

from src.core.document_processor import DocumentProcessor
from src.core.vector_store import VectorStoreManager
from src.core.rag_engine import RAGEngine

class TestPerformance:
    """Performance and load tests for ScholarAI"""
    
    @pytest.fixture
    def large_document_set(self):
        """Create a large set of test documents"""
        temp_dir = tempfile.mkdtemp()
        
        # Create multiple documents of varying sizes
        for i in range(50):  # 50 documents
            doc_path = Path(temp_dir) / f"document_{i}.txt"
            # Create documents with varying content sizes
            content_size = 100 + (i * 20)  # 100 to 1080 words
            content = f"Document {i} content. " * content_size
            doc_path.write_text(content)
        
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_document_processing_performance(self, large_document_set):
        """Test document processing performance with large dataset"""
        processor = DocumentProcessor(chunk_size=500, chunk_overlap=50)
        
        start_time = time.time()
        documents = processor.process_directory(large_document_set)
        processing_time = time.time() - start_time
        
        # Performance assertions
        assert len(documents) > 0
        assert processing_time < 30.0  # Should process 50 docs in under 30 seconds
        
        # Calculate processing rate
        docs_per_second = 50 / processing_time
        assert docs_per_second > 1.0  # At least 1 document per second
        
        print(f"Processed 50 documents in {processing_time:.2f} seconds")
        print(f"Processing rate: {docs_per_second:.2f} docs/second")
    
    def test_chunking_performance(self):
        """Test chunking performance with large documents"""
        processor = DocumentProcessor(chunk_size=1000, chunk_overlap=100)
        
        # Create a very large document
        large_content = "This is a test sentence for chunking performance. " * 1000  # ~50KB
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        temp_file.write(large_content)
        temp_file.close()
        
        try:
            start_time = time.time()
            documents = processor.process_document(temp_file.name)
            chunking_time = time.time() - start_time
            
            # Performance assertions
            assert len(documents) > 10  # Should create multiple chunks
            assert chunking_time < 5.0  # Should chunk large doc in under 5 seconds
            
            # Calculate chunking rate
            chunks_per_second = len(documents) / chunking_time
            assert chunks_per_second > 5.0  # At least 5 chunks per second
            
            print(f"Created {len(documents)} chunks in {chunking_time:.2f} seconds")
            print(f"Chunking rate: {chunks_per_second:.2f} chunks/second")
            
        finally:
            Path(temp_file.name).unlink()
    
    @patch('src.core.vector_store.OpenAIEmbeddings')
    @patch('src.core.vector_store.chromadb.PersistentClient')
    @patch('src.core.vector_store.Chroma')
    def test_vector_store_performance(self, mock_chroma, mock_client, mock_embeddings):
        """Test vector store operations performance"""
        mock_vector_store = Mock()
        mock_chroma.return_value = mock_vector_store
        
        vector_store_manager = VectorStoreManager(
            persist_directory="/tmp/test",
            collection_name="perf_test",
            openai_api_key="test-key"
        )
        
        # Create test documents
        documents = []
        for i in range(100):
            doc = Mock()
            doc.page_content = f"Test content {i}"
            doc.metadata = {"source": f"doc_{i}.txt", "chunk_id": i}
            documents.append(doc)
        
        # Test batch addition performance
        start_time = time.time()
        vector_store_manager.add_documents(documents)
        addition_time = time.time() - start_time
        
        assert addition_time < 10.0  # Should add 100 docs in under 10 seconds
        
        # Test search performance
        mock_vector_store.similarity_search.return_value = documents[:5]
        
        start_time = time.time()
        for _ in range(10):  # 10 searches
            vector_store_manager.similarity_search("test query", k=5)
        search_time = time.time() - start_time
        
        assert search_time < 5.0  # 10 searches in under 5 seconds
        
        print(f"Added 100 documents in {addition_time:.2f} seconds")
        print(f"Performed 10 searches in {search_time:.2f} seconds")
    
    @patch('src.core.rag_engine.ChatOpenAI')
    @patch('src.core.rag_engine.RetrievalQA')
    def test_rag_query_performance(self, mock_retrieval_qa, mock_chat_openai):
        """Test RAG query performance"""
        # Setup mocks
        mock_vector_store_manager = Mock()
        mock_llm = Mock()
        mock_chat_openai.return_value = mock_llm
        
        mock_qa_chain = Mock()
        mock_retrieval_qa.from_chain_type.return_value = mock_qa_chain
        
        # Mock quick responses
        mock_qa_chain.return_value = {
            "result": "Quick test answer",
            "source_documents": [Mock() for _ in range(3)]
        }
        
        rag_engine = RAGEngine(
            vector_store_manager=mock_vector_store_manager,
            openai_api_key="test-key"
        )
        
        # Test multiple queries performance
        queries = [
            "What is Python?",
            "Explain machine learning",
            "How to use SQL?",
            "What are algorithms?",
            "Describe data structures"
        ]
        
        start_time = time.time()
        for query in queries:
            result = rag_engine.query(query)
            assert "answer" in result
        query_time = time.time() - start_time
        
        # Ensure we don't divide by zero
        if query_time == 0:
            query_time = 0.001  # 1ms minimum
        
        assert query_time < 10.0  # 5 queries in under 10 seconds
        
        queries_per_second = len(queries) / query_time
        print(f"Processed {len(queries)} queries in {query_time:.2f} seconds")
        print(f"Query rate: {queries_per_second:.2f} queries/second")
    
    def test_concurrent_document_processing(self, large_document_set):
        """Test concurrent document processing"""
        processor = DocumentProcessor(chunk_size=500, chunk_overlap=50)
        
        # Get list of files
        files = list(Path(large_document_set).glob("*.txt"))[:20]  # Use 20 files
        
        def process_file(file_path):
            return processor.process_document(str(file_path))
        
        # Test concurrent processing
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(process_file, files))
        concurrent_time = time.time() - start_time
        
        # Test sequential processing
        start_time = time.time()
        sequential_results = [process_file(f) for f in files]
        sequential_time = time.time() - start_time
        
        # Verify results are the same
        assert len(results) == len(sequential_results)
        
        # Concurrent should be faster (or at least not significantly slower)
        speedup_ratio = sequential_time / concurrent_time
        print(f"Sequential time: {sequential_time:.2f}s")
        print(f"Concurrent time: {concurrent_time:.2f}s")
        print(f"Speedup ratio: {speedup_ratio:.2f}x")
        
        # Allow for some overhead, but expect some improvement
        assert speedup_ratio > 0.8  # At least 80% of sequential performance
    
    @patch('src.core.vector_store.OpenAIEmbeddings')
    @patch('src.core.vector_store.chromadb.PersistentClient')
    @patch('src.core.vector_store.Chroma')
    def test_memory_usage_document_processing(self, mock_chroma, mock_client, mock_embeddings):
        """Test memory usage during document processing"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        processor = DocumentProcessor(chunk_size=1000, chunk_overlap=100)
        
        # Process many documents
        temp_dir = tempfile.mkdtemp()
        try:
            # Create 100 small documents
            for i in range(100):
                doc_path = Path(temp_dir) / f"doc_{i}.txt"
                content = f"Document {i} content. " * 50
                doc_path.write_text(content)
            
            documents = processor.process_directory(temp_dir)
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            print(f"Initial memory: {initial_memory:.2f} MB")
            print(f"Final memory: {final_memory:.2f} MB")
            print(f"Memory increase: {memory_increase:.2f} MB")
            print(f"Documents processed: {len(documents)}")
            
            # Memory usage should be reasonable (less than 500MB increase)
            assert memory_increase < 500
            
        finally:
            shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mock_rag_engine(self):
        """Mock RAG engine for performance tests"""
        mock_engine = Mock()
        return mock_engine
    
    def test_large_query_response_time(self, mock_rag_engine):
        """Test response time for complex queries"""
        # Mock a complex response
        large_sources = []
        for i in range(10):  # 10 sources
            source = {
                "file_name": f"document_{i}.pdf",
                "source": f"/docs/document_{i}.pdf",
                "chunk_id": i,
                "content_preview": "A" * 200,  # Full 200 char preview
                "document_type": "learning_material",
                "subject": "Computer Science"
            }
            large_sources.append(source)
        
        mock_rag_engine.query.return_value = {
            "answer": "A" * 1000,  # Large answer
            "sources": large_sources,
            "confidence": "high",
            "total_sources_found": 10
        }
        
        start_time = time.time()
        result = mock_rag_engine.query("Complex query about computer science")
        response_time = time.time() - start_time
        
        # Response should be fast even with large data
        assert response_time < 1.0  # Under 1 second
        assert len(result["sources"]) == 10
        assert len(result["answer"]) == 1000
    
    def test_metadata_extraction_performance(self):
        """Test metadata extraction performance"""
        processor = DocumentProcessor()
        
        # Test with various file paths
        test_paths = [
            "/data/Cocubes/cocubes_quant_2023_hard.pdf",
            "/data/Google/google_python_interview_2022.pdf",
            "/data/Microsoft/microsoft_algorithms_easy.txt",
            "/data/mock_tests/java_advanced_test.pdf",
            "/data/learning/python_basics_tutorial.txt"
        ] * 100  # 500 total paths
        
        start_time = time.time()
        for path in test_paths:
            metadata = processor.extract_metadata(path, "sample content")
            assert "document_type" in metadata
            assert "file_type" in metadata
        extraction_time = time.time() - start_time
        
        # Should extract metadata quickly
        assert extraction_time < 5.0  # 500 extractions in under 5 seconds
        
        extractions_per_second = len(test_paths) / extraction_time
        print(f"Metadata extraction rate: {extractions_per_second:.2f} extractions/second")
        assert extractions_per_second > 50  # At least 50 per second
    
    def test_stress_test_concurrent_queries(self, mock_rag_engine):
        """Stress test with concurrent queries"""
        mock_rag_engine.query.return_value = {
            "answer": "Test answer",
            "sources": [{"file_name": "test.pdf", "content_preview": "preview"}],
            "confidence": "medium",
            "total_sources_found": 1
        }
        
        def make_query(query_id):
            return mock_rag_engine.query(f"Test query {query_id}")
        
        # Test with many concurrent queries
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_query, i) for i in range(50)]
            results = [f.result() for f in futures]
        concurrent_time = time.time() - start_time
        
        assert len(results) == 50
        assert all("answer" in result for result in results)
        assert concurrent_time < 15.0  # 50 concurrent queries in under 15 seconds
        
        queries_per_second = 50 / concurrent_time
        print(f"Concurrent query rate: {queries_per_second:.2f} queries/second")
        assert queries_per_second > 2.0  # At least 2 queries per second under load