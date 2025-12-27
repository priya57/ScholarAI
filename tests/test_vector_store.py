import pytest
from unittest.mock import Mock, patch, MagicMock
from src.core.vector_store import VectorStoreManager
from langchain.schema import Document

class TestVectorStoreManager:
    
    @patch('src.core.vector_store.OpenAIEmbeddings')
    @patch('src.core.vector_store.chromadb.PersistentClient')
    @patch('src.core.vector_store.Chroma')
    @patch('os.makedirs')
    def test_init(self, mock_makedirs, mock_chroma, mock_client, mock_embeddings):
        """Test VectorStoreManager initialization"""
        manager = VectorStoreManager(
            persist_directory="/test/dir",
            collection_name="test_collection",
            openai_api_key="test-key"
        )
        
        mock_makedirs.assert_called_once_with("/test/dir", exist_ok=True)
        mock_embeddings.assert_called_once_with(openai_api_key="test-key")
        mock_client.assert_called_once()
        mock_chroma.assert_called_once()
    
    def test_add_documents_empty_list(self, mock_vector_store_manager):
        """Test adding empty document list"""
        mock_vector_store_manager.add_documents([])
        # Should not raise any errors
    
    def test_add_documents_success(self, mock_vector_store_manager, capsys):
        """Test successful document addition"""
        documents = [
            Document(page_content="Test content 1", metadata={"source": "test1.pdf"}),
            Document(page_content="Test content 2", metadata={"source": "test2.pdf"})
        ]
        
        mock_vector_store_manager.vector_store.add_documents = Mock()
        mock_vector_store_manager.add_documents(documents)
        
        mock_vector_store_manager.vector_store.add_documents.assert_called_once_with(documents)
        captured = capsys.readouterr()
        assert "Added 2 documents to vector store" in captured.out
    
    def test_similarity_search_with_filters(self, mock_vector_store_manager):
        """Test similarity search with metadata filters"""
        mock_vector_store_manager.vector_store.similarity_search = Mock(return_value=[])
        
        filters = {"document_type": "placement_paper"}
        result = mock_vector_store_manager.similarity_search_with_filters(
            "test query", k=3, filters=filters
        )
        
        mock_vector_store_manager.vector_store.similarity_search.assert_called_once_with(
            "test query", k=3, filter=filters
        )
    
    def test_similarity_search_without_filters(self, mock_vector_store_manager):
        """Test similarity search without filters"""
        mock_vector_store_manager.vector_store.similarity_search = Mock(return_value=[])
        
        result = mock_vector_store_manager.similarity_search_with_filters("test query", k=5)
        
        mock_vector_store_manager.vector_store.similarity_search.assert_called_once_with(
            "test query", k=5
        )
    
    def test_filter_by_document_type(self, mock_vector_store_manager):
        """Test filtering by document type"""
        mock_vector_store_manager.similarity_search_with_filters = Mock(return_value=[])
        
        result = mock_vector_store_manager.filter_by_document_type("query", "mock_test", k=3)
        
        mock_vector_store_manager.similarity_search_with_filters.assert_called_once_with(
            "query", 3, {"document_type": "mock_test"}
        )
    
    def test_filter_by_company(self, mock_vector_store_manager):
        """Test filtering by company"""
        mock_vector_store_manager.similarity_search_with_filters = Mock(return_value=[])
        
        result = mock_vector_store_manager.filter_by_company("query", "Google", k=4)
        
        mock_vector_store_manager.similarity_search_with_filters.assert_called_once_with(
            "query", 4, {"company": "Google"}
        )
    
    def test_filter_by_subject(self, mock_vector_store_manager):
        """Test filtering by subject"""
        mock_vector_store_manager.similarity_search_with_filters = Mock(return_value=[])
        
        result = mock_vector_store_manager.filter_by_subject("query", "Python")
        
        mock_vector_store_manager.similarity_search_with_filters.assert_called_once_with(
            "query", 5, {"subject": "Python"}
        )
    
    def test_filter_by_difficulty(self, mock_vector_store_manager):
        """Test filtering by difficulty"""
        mock_vector_store_manager.similarity_search_with_filters = Mock(return_value=[])
        
        result = mock_vector_store_manager.filter_by_difficulty("query", "hard")
        
        mock_vector_store_manager.similarity_search_with_filters.assert_called_once_with(
            "query", 5, {"difficulty": "hard"}
        )
    
    def test_get_available_filters_success(self, mock_vector_store_manager):
        """Test getting available filters"""
        mock_collection = Mock()
        mock_collection.get.return_value = {
            "metadatas": [
                {"document_type": "placement_paper", "company": "Google", "subject": "Python"},
                {"document_type": "mock_test", "company": "Microsoft", "subject": "Java"},
                {"document_type": "placement_paper", "company": "Google", "difficulty": "hard"}
            ]
        }
        mock_vector_store_manager.client.get_collection = Mock(return_value=mock_collection)
        
        filters = mock_vector_store_manager.get_available_filters()
        
        assert "Google" in filters["companies"]
        assert "Microsoft" in filters["companies"]
        assert "placement_paper" in filters["document_types"]
        assert "mock_test" in filters["document_types"]
        assert "Python" in filters["subjects"]
        assert "Java" in filters["subjects"]
    
    def test_get_available_filters_error(self, mock_vector_store_manager):
        """Test getting available filters with error"""
        mock_vector_store_manager.client.get_collection = Mock(side_effect=Exception("Error"))
        
        filters = mock_vector_store_manager.get_available_filters()
        
        assert filters == {}
    
    def test_similarity_search(self, mock_vector_store_manager):
        """Test basic similarity search"""
        mock_vector_store_manager.vector_store.similarity_search = Mock(return_value=[])
        
        result = mock_vector_store_manager.similarity_search("test query", k=3)
        
        mock_vector_store_manager.vector_store.similarity_search.assert_called_once_with(
            "test query", k=3
        )
    
    def test_similarity_search_with_score(self, mock_vector_store_manager):
        """Test similarity search with scores"""
        mock_vector_store_manager.vector_store.similarity_search_with_score = Mock(return_value=[])
        
        result = mock_vector_store_manager.similarity_search_with_score("test query", k=4)
        
        mock_vector_store_manager.vector_store.similarity_search_with_score.assert_called_once_with(
            "test query", k=4
        )
    
    def test_get_collection_count_success(self, mock_vector_store_manager):
        """Test getting collection count"""
        mock_collection = Mock()
        mock_collection.count.return_value = 100
        mock_vector_store_manager.client.get_collection = Mock(return_value=mock_collection)
        
        count = mock_vector_store_manager.get_collection_count()
        
        assert count == 100
    
    def test_get_collection_count_error(self, mock_vector_store_manager):
        """Test getting collection count with error"""
        mock_vector_store_manager.client.get_collection = Mock(side_effect=Exception("Error"))
        
        count = mock_vector_store_manager.get_collection_count()
        
        assert count == 0
    
    def test_delete_collection_success(self, mock_vector_store_manager, capsys):
        """Test successful collection deletion"""
        mock_vector_store_manager.client.delete_collection = Mock()
        
        mock_vector_store_manager.delete_collection()
        
        mock_vector_store_manager.client.delete_collection.assert_called_once_with(
            mock_vector_store_manager.collection_name
        )
        captured = capsys.readouterr()
        assert "Deleted collection" in captured.out
    
    def test_delete_collection_error(self, mock_vector_store_manager, capsys):
        """Test collection deletion with error"""
        mock_vector_store_manager.client.delete_collection = Mock(side_effect=Exception("Delete error"))
        
        mock_vector_store_manager.delete_collection()
        
        captured = capsys.readouterr()
        assert "Error deleting collection" in captured.out
    
    @patch('src.core.vector_store.Chroma')
    def test_reset_collection(self, mock_chroma, mock_vector_store_manager):
        """Test collection reset"""
        mock_vector_store_manager.delete_collection = Mock()
        
        mock_vector_store_manager.reset_collection()
        
        mock_vector_store_manager.delete_collection.assert_called_once()
        mock_chroma.assert_called()