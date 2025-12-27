import pytest
from unittest.mock import Mock, patch, MagicMock
from src.core.rag_engine import RAGEngine
from langchain.schema import Document

class TestRAGEngine:
    
    @patch('src.core.rag_engine.ChatOpenAI')
    @patch('src.core.rag_engine.RetrievalQA')
    def test_init(self, mock_retrieval_qa, mock_chat_openai, mock_vector_store_manager):
        """Test RAGEngine initialization"""
        engine = RAGEngine(
            vector_store_manager=mock_vector_store_manager,
            openai_api_key="test-key",
            model_name="gpt-4"
        )
        
        mock_chat_openai.assert_called_once_with(
            openai_api_key="test-key",
            model_name="gpt-4",
            temperature=0.1
        )
        mock_retrieval_qa.from_chain_type.assert_called_once()
    
    def test_query_with_docs_empty_docs(self, mock_rag_engine):
        """Test query with empty document list"""
        result = mock_rag_engine.query_with_docs("What is Python?", [])
        
        assert "couldn't find any relevant information" in result["answer"]
        assert result["sources"] == []
        assert result["confidence"] == "low"
        assert result["total_sources_found"] == 0
    
    def test_query_with_docs_success(self, mock_rag_engine):
        """Test successful query with documents"""
        docs = [
            Document(
                page_content="Python is a programming language",
                metadata={
                    "file_name": "python_guide.pdf",
                    "source": "/docs/python_guide.pdf",
                    "chunk_id": 0,
                    "document_type": "learning_material",
                    "subject": "Python"
                }
            ),
            Document(
                page_content="Python is used for web development",
                metadata={
                    "file_name": "web_dev.pdf",
                    "source": "/docs/web_dev.pdf",
                    "chunk_id": 1,
                    "document_type": "learning_material",
                    "subject": "Python"
                }
            )
        ]
        
        mock_rag_engine.llm.predict = Mock(return_value="Python is a versatile programming language.")
        
        result = mock_rag_engine.query_with_docs("What is Python?", docs)
        
        assert result["answer"] == "Python is a versatile programming language."
        assert len(result["sources"]) == 2
        assert result["confidence"] == "medium"  # Less than 3 docs
        assert result["total_sources_found"] == 2
        
        # Check source information
        source = result["sources"][0]
        assert source["file_name"] == "python_guide.pdf"
        assert source["document_type"] == "learning_material"
        assert "Python is a programming" in source["content_preview"]
    
    def test_query_with_docs_high_confidence(self, mock_rag_engine):
        """Test query with high confidence (3+ docs)"""
        docs = [Mock() for _ in range(3)]  # 3 documents for high confidence
        for i, doc in enumerate(docs):
            doc.page_content = f"Content {i}"
            doc.metadata = {"file_name": f"doc{i}.pdf", "chunk_id": i}
        
        mock_rag_engine.llm.predict = Mock(return_value="Test answer")
        
        result = mock_rag_engine.query_with_docs("Test question", docs)
        
        assert result["confidence"] == "high"
    
    def test_query_with_docs_error(self, mock_rag_engine):
        """Test query with documents when error occurs"""
        docs = [Mock()]
        mock_rag_engine.llm.predict = Mock(side_effect=Exception("API Error"))
        
        result = mock_rag_engine.query_with_docs("Test question", docs)
        
        assert "encountered an error" in result["answer"]
        assert result["confidence"] == "low"
        assert "error" in result
    
    def test_query_success(self, mock_rag_engine):
        """Test successful query"""
        mock_result = {
            "result": "Python is a programming language",
            "source_documents": [
                Mock(
                    page_content="Python content",
                    metadata={
                        "file_name": "python.pdf",
                        "source": "/docs/python.pdf",
                        "chunk_id": 0,
                        "document_type": "learning_material"
                    }
                )
            ]
        }
        
        mock_rag_engine.qa_chain = Mock(return_value=mock_result)
        
        result = mock_rag_engine.query("What is Python?", max_docs=3)
        
        assert result["answer"] == "Python is a programming language"
        assert len(result["sources"]) == 1
        assert result["confidence"] == "medium"  # Less than 3 docs
        assert result["total_sources_found"] == 1
    
    def test_query_high_confidence(self, mock_rag_engine):
        """Test query with high confidence"""
        source_docs = [Mock() for _ in range(3)]
        for i, doc in enumerate(source_docs):
            doc.page_content = f"Content {i}"
            doc.metadata = {"file_name": f"doc{i}.pdf", "chunk_id": i}
        
        mock_result = {
            "result": "Test answer",
            "source_documents": source_docs
        }
        
        mock_rag_engine.qa_chain = Mock(return_value=mock_result)
        
        result = mock_rag_engine.query("Test question")
        
        assert result["confidence"] == "high"
    
    def test_query_error(self, mock_rag_engine):
        """Test query with error"""
        mock_rag_engine.qa_chain = Mock(side_effect=Exception("Query error"))
        
        result = mock_rag_engine.query("Test question")
        
        assert "encountered an error" in result["answer"]
        assert result["confidence"] == "low"
        assert "error" in result
    
    def test_get_relevant_documents(self, mock_rag_engine):
        """Test getting relevant documents"""
        mock_doc = Mock()
        mock_doc.page_content = "Test content"
        mock_doc.metadata = {"source": "test.pdf"}
        
        mock_rag_engine.vector_store_manager.similarity_search_with_score = Mock(
            return_value=[(mock_doc, 0.8)]
        )
        
        result = mock_rag_engine.get_relevant_documents("test query", k=3)
        
        assert len(result) == 1
        assert result[0]["content"] == "Test content"
        assert result[0]["metadata"] == {"source": "test.pdf"}
        assert result[0]["relevance_score"] == 0.8
    
    def test_update_retriever_config(self, mock_rag_engine):
        """Test updating retriever configuration"""
        mock_rag_engine.qa_chain.retriever = Mock()
        mock_rag_engine.qa_chain.retriever.search_kwargs = {}
        
        mock_rag_engine.update_retriever_config(k=10, score_threshold=0.9)
        
        expected_kwargs = {"k": 10, "score_threshold": 0.9}
        assert mock_rag_engine.qa_chain.retriever.search_kwargs == expected_kwargs
    
    def test_content_preview_truncation(self, mock_rag_engine):
        """Test content preview truncation"""
        long_content = "a" * 300  # Content longer than 200 chars
        docs = [
            Document(
                page_content=long_content,
                metadata={"file_name": "test.pdf", "chunk_id": 0}
            )
        ]
        
        mock_rag_engine.llm.predict = Mock(return_value="Test answer")
        
        result = mock_rag_engine.query_with_docs("Test question", docs)
        
        preview = result["sources"][0]["content_preview"]
        assert len(preview) <= 203  # 200 chars + "..."
        assert preview.endswith("...")
    
    def test_content_preview_no_truncation(self, mock_rag_engine):
        """Test content preview without truncation"""
        short_content = "Short content"
        docs = [
            Document(
                page_content=short_content,
                metadata={"file_name": "test.pdf", "chunk_id": 0}
            )
        ]
        
        mock_rag_engine.llm.predict = Mock(return_value="Test answer")
        
        result = mock_rag_engine.query_with_docs("Test question", docs)
        
        preview = result["sources"][0]["content_preview"]
        assert preview == short_content
        assert not preview.endswith("...")
    
    def test_prompt_template_format(self, mock_rag_engine):
        """Test prompt template formatting"""
        context = "Python is a programming language"
        question = "What is Python?"
        
        formatted_prompt = mock_rag_engine.prompt_template.format(
            context=context, question=question
        )
        
        assert context in formatted_prompt
        assert question in formatted_prompt
        assert "AI assistant helping students" in formatted_prompt