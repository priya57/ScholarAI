import pytest
from unittest.mock import Mock, patch, call
import sys
from pathlib import Path
import argparse

# Add src to path for testing
sys.path.append(str(Path(__file__).parent.parent / "src"))

import cli

class TestCLI:
    
    @patch('cli.init_components')
    def test_init_components(self, mock_init):
        """Test component initialization"""
        mock_processor = Mock()
        mock_vector_store = Mock()
        mock_rag_engine = Mock()
        mock_init.return_value = (mock_processor, mock_vector_store, mock_rag_engine)
        
        result = cli.init_components()
        
        assert len(result) == 3
        mock_init.assert_called_once()
    
    @patch('cli.init_components')
    @patch('os.path.exists')
    def test_ingest_documents_directory_not_exists(self, mock_exists, mock_init, capsys):
        """Test ingesting from non-existent directory"""
        mock_exists.return_value = False
        
        cli.ingest_documents("/nonexistent/path")
        
        captured = capsys.readouterr()
        assert "Error: Directory /nonexistent/path does not exist" in captured.out
        mock_init.assert_not_called()
    
    @patch('cli.init_components')
    @patch('os.path.exists')
    def test_ingest_documents_success(self, mock_exists, mock_init, capsys):
        """Test successful document ingestion"""
        mock_exists.return_value = True
        mock_processor = Mock()
        mock_vector_store = Mock()
        mock_rag_engine = Mock()
        mock_init.return_value = (mock_processor, mock_vector_store, mock_rag_engine)
        
        # Mock document processing
        mock_documents = [Mock(), Mock(), Mock()]
        mock_processor.process_directory.return_value = mock_documents
        
        cli.ingest_documents("/test/path")
        
        captured = capsys.readouterr()
        assert "Processing documents from: /test/path" in captured.out
        assert "Document ingestion completed successfully!" in captured.out
        
        mock_processor.process_directory.assert_called_once_with("/test/path")
        mock_vector_store.add_documents.assert_called_once_with(mock_documents)
    
    @patch('cli.init_components')
    @patch('os.path.exists')
    def test_ingest_documents_no_documents(self, mock_exists, mock_init, capsys):
        """Test ingestion when no documents found"""
        mock_exists.return_value = True
        mock_processor = Mock()
        mock_vector_store = Mock()
        mock_rag_engine = Mock()
        mock_init.return_value = (mock_processor, mock_vector_store, mock_rag_engine)
        
        # Mock empty document processing
        mock_processor.process_directory.return_value = []
        
        cli.ingest_documents("/test/path")
        
        captured = capsys.readouterr()
        assert "No documents found or processed" in captured.out
        mock_vector_store.add_documents.assert_not_called()
    
    @patch('cli.init_components')
    def test_query_system_success(self, mock_init, capsys):
        """Test successful system query"""
        mock_processor = Mock()
        mock_vector_store = Mock()
        mock_rag_engine = Mock()
        mock_init.return_value = (mock_processor, mock_vector_store, mock_rag_engine)
        
        # Mock query result
        mock_result = {
            "answer": "Python is a programming language",
            "sources": [
                {
                    "file_name": "python_guide.pdf",
                    "content_preview": "Python is a high-level programming language..."
                },
                {
                    "file_name": "programming_basics.pdf",
                    "content_preview": "Programming languages are tools for..."
                }
            ]
        }
        mock_rag_engine.query.return_value = mock_result
        
        cli.query_system("What is Python?")
        
        captured = capsys.readouterr()
        assert "Question: What is Python?" in captured.out
        assert "ANSWER:" in captured.out
        assert "Python is a programming language" in captured.out
        assert "SOURCES:" in captured.out
        assert "python_guide.pdf" in captured.out
        assert "programming_basics.pdf" in captured.out
        
        mock_rag_engine.query.assert_called_once_with("What is Python?")
    
    @patch('cli.init_components')
    def test_query_system_no_sources(self, mock_init, capsys):
        """Test query with no sources"""
        mock_processor = Mock()
        mock_vector_store = Mock()
        mock_rag_engine = Mock()
        mock_init.return_value = (mock_processor, mock_vector_store, mock_rag_engine)
        
        # Mock query result with no sources
        mock_result = {
            "answer": "I don't have information about that topic.",
            "sources": []
        }
        mock_rag_engine.query.return_value = mock_result
        
        cli.query_system("Unknown topic")
        
        captured = capsys.readouterr()
        assert "ANSWER:" in captured.out
        assert "I don't have information about that topic." in captured.out
        assert "SOURCES:" not in captured.out
    
    @patch('cli.init_components')
    @patch('builtins.input')
    def test_reset_system_confirmed(self, mock_input, mock_init, capsys):
        """Test system reset when confirmed"""
        mock_input.return_value = 'y'
        mock_processor = Mock()
        mock_vector_store = Mock()
        mock_rag_engine = Mock()
        mock_init.return_value = (mock_processor, mock_vector_store, mock_rag_engine)
        
        cli.reset_system()
        
        captured = capsys.readouterr()
        assert "Vector store reset successfully!" in captured.out
        mock_vector_store.reset_collection.assert_called_once()
    
    @patch('cli.init_components')
    @patch('builtins.input')
    def test_reset_system_cancelled(self, mock_input, mock_init, capsys):
        """Test system reset when cancelled"""
        mock_input.return_value = 'n'
        mock_processor = Mock()
        mock_vector_store = Mock()
        mock_rag_engine = Mock()
        mock_init.return_value = (mock_processor, mock_vector_store, mock_rag_engine)
        
        cli.reset_system()
        
        captured = capsys.readouterr()
        assert "Reset cancelled" in captured.out
        mock_vector_store.reset_collection.assert_not_called()
    
    @patch('cli.init_components')
    def test_show_stats(self, mock_init, capsys):
        """Test showing system statistics"""
        mock_processor = Mock()
        mock_vector_store = Mock()
        mock_rag_engine = Mock()
        mock_init.return_value = (mock_processor, mock_vector_store, mock_rag_engine)
        
        mock_vector_store.get_collection_count.return_value = 150
        
        with patch('cli.settings') as mock_settings:
            mock_settings.collection_name = "test_collection"
            mock_settings.chunk_size = 1000
            mock_settings.llm_model = "gpt-3.5-turbo"
            
            cli.show_stats()
        
        captured = capsys.readouterr()
        assert "System Statistics:" in captured.out
        assert "Total document chunks: 150" in captured.out
        assert "Collection name: test_collection" in captured.out
        assert "Chunk size: 1000" in captured.out
        assert "Model: gpt-3.5-turbo" in captured.out
    
    @patch('sys.argv', ['cli.py', 'ingest', '/test/path'])
    @patch('cli.ingest_documents')
    def test_main_ingest_command(self, mock_ingest):
        """Test main function with ingest command"""
        cli.main()
        mock_ingest.assert_called_once_with('/test/path')
    
    @patch('sys.argv', ['cli.py', 'query', 'What is Python?'])
    @patch('cli.query_system')
    def test_main_query_command(self, mock_query):
        """Test main function with query command"""
        cli.main()
        mock_query.assert_called_once_with('What is Python?')
    
    @patch('sys.argv', ['cli.py', 'reset'])
    @patch('cli.reset_system')
    def test_main_reset_command(self, mock_reset):
        """Test main function with reset command"""
        cli.main()
        mock_reset.assert_called_once()
    
    @patch('sys.argv', ['cli.py', 'stats'])
    @patch('cli.show_stats')
    def test_main_stats_command(self, mock_stats):
        """Test main function with stats command"""
        cli.main()
        mock_stats.assert_called_once()
    
    @patch('sys.argv', ['cli.py'])
    @patch('argparse.ArgumentParser.print_help')
    def test_main_no_command(self, mock_help):
        """Test main function with no command"""
        cli.main()
        mock_help.assert_called_once()
    
    @patch('sys.argv', ['cli.py', '--help'])
    def test_main_help(self):
        """Test main function with help"""
        with pytest.raises(SystemExit):
            cli.main()
    
    def test_argument_parser_setup(self):
        """Test argument parser configuration"""
        parser = argparse.ArgumentParser(description="ScholarAI RAG System CLI")
        subparsers = parser.add_subparsers(dest="command", help="Available commands")
        
        # Test ingest subparser
        ingest_parser = subparsers.add_parser("ingest", help="Ingest documents from directory")
        ingest_parser.add_argument("directory", help="Directory containing documents to ingest")
        
        # Test query subparser
        query_parser = subparsers.add_parser("query", help="Query the RAG system")
        query_parser.add_argument("question", help="Question to ask the system")
        
        # Test reset subparser
        subparsers.add_parser("reset", help="Reset the vector store")
        
        # Test stats subparser
        subparsers.add_parser("stats", help="Show system statistics")
        
        # Test parsing
        args = parser.parse_args(['ingest', '/test/path'])
        assert args.command == 'ingest'
        assert args.directory == '/test/path'
        
        args = parser.parse_args(['query', 'What is Python?'])
        assert args.command == 'query'
        assert args.question == 'What is Python?'
        
        args = parser.parse_args(['reset'])
        assert args.command == 'reset'
        
        args = parser.parse_args(['stats'])
        assert args.command == 'stats'