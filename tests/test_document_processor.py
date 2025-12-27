import pytest
from pathlib import Path
from unittest.mock import patch, mock_open, Mock
from src.core.document_processor import DocumentProcessor

class TestDocumentProcessor:
    
    def test_init(self):
        """Test DocumentProcessor initialization"""
        processor = DocumentProcessor(chunk_size=500, chunk_overlap=100)
        assert processor.text_splitter._chunk_size == 500
        assert processor.text_splitter._chunk_overlap == 100
    
    def test_extract_metadata_placement_paper(self):
        """Test metadata extraction for placement papers"""
        processor = DocumentProcessor()
        file_path = "/data/Cocubes/cocubes_quant_2023.pdf"
        content = "Sample content"
        
        metadata = processor.extract_metadata(file_path, content)
        
        assert metadata["document_type"] == "placement_paper"
        assert metadata["company"] == "Cocubes"
        assert metadata["year"] == "2023"
        assert metadata["subject"] == "Quantitative Aptitude"
        assert metadata["file_type"] == ".pdf"
    
    def test_extract_metadata_mock_test(self):
        """Test metadata extraction for mock tests"""
        processor = DocumentProcessor()
        file_path = "/data/mock_test_java_hard.pdf"
        content = "Sample content"
        
        metadata = processor.extract_metadata(file_path, content)
        
        assert metadata["document_type"] == "mock_test"
        assert metadata["subject"] == "Java"
        assert metadata["difficulty"] == "hard"
    
    def test_extract_metadata_learning_material(self):
        """Test metadata extraction for learning materials"""
        processor = DocumentProcessor()
        file_path = "/data/algorithms_tutorial.pdf"
        content = "Sample content"
        
        metadata = processor.extract_metadata(file_path, content)
        
        assert metadata["document_type"] == "learning_material"
        assert metadata["subject"] == "Algorithms"
        assert metadata["difficulty"] == "medium"
    
    def test_extract_text_from_txt(self, sample_txt_path):
        """Test text extraction from TXT files"""
        processor = DocumentProcessor()
        text = processor.extract_text_from_txt(sample_txt_path)
        
        assert "test document" in text.lower()
        assert len(text) > 0
    
    @patch('builtins.open', mock_open(read_data="Sample RTF content"))
    @patch('src.core.document_processor.RTF_AVAILABLE', True)
    @patch('src.core.document_processor.rtf_to_text')
    def test_extract_text_from_rtf(self, mock_rtf_to_text):
        """Test text extraction from RTF files"""
        mock_rtf_to_text.return_value = "Converted RTF text"
        processor = DocumentProcessor()
        
        text = processor.extract_text_from_rtf("test.rtf")
        
        assert text == "Converted RTF text"
        mock_rtf_to_text.assert_called_once()
    
    @patch('src.core.document_processor.RTF_AVAILABLE', False)
    def test_extract_text_from_rtf_unavailable(self):
        """Test RTF extraction when library unavailable"""
        processor = DocumentProcessor()
        text = processor.extract_text_from_rtf("test.rtf")
        
        assert "RTF file" in text
        assert "striprtf not available" in text
    
    @patch('src.core.document_processor.OCR_AVAILABLE', False)
    def test_extract_text_from_image_unavailable(self):
        """Test image extraction when OCR unavailable"""
        processor = DocumentProcessor()
        text = processor.extract_text_from_image("test.jpg")
        
        assert "Image file" in text
        assert "OCR not available" in text
    
    def test_process_document_txt(self, sample_txt_path):
        """Test document processing for TXT files"""
        processor = DocumentProcessor(chunk_size=50, chunk_overlap=10)
        documents = processor.process_document(sample_txt_path)
        
        assert len(documents) > 0
        assert all(hasattr(doc, 'page_content') for doc in documents)
        assert all(hasattr(doc, 'metadata') for doc in documents)
        assert documents[0].metadata["file_type"] == ".txt"
    
    def test_process_document_unsupported_format(self, temp_dir):
        """Test processing unsupported file format"""
        processor = DocumentProcessor()
        unsupported_file = Path(temp_dir) / "test.xyz"
        unsupported_file.write_text("content")
        
        with pytest.raises(ValueError, match="Unsupported file format"):
            processor.process_document(str(unsupported_file))
    
    @patch('os.walk')
    @patch.object(DocumentProcessor, 'process_document')
    def test_process_directory(self, mock_process_doc, mock_walk):
        """Test directory processing"""
        mock_walk.return_value = [
            ("/test", [], ["doc1.pdf", "doc2.txt", "ignore.xyz"])
        ]
        mock_process_doc.return_value = [Mock()]
        
        processor = DocumentProcessor()
        documents = processor.process_directory("/test")
        
        assert len(documents) == 2  # Only supported formats
        assert mock_process_doc.call_count == 2
    
    @patch('os.walk')
    @patch.object(DocumentProcessor, 'process_document')
    def test_process_directory_with_errors(self, mock_process_doc, mock_walk, capsys):
        """Test directory processing with errors"""
        mock_walk.return_value = [
            ("/test", [], ["doc1.pdf", "doc2.txt"])
        ]
        mock_process_doc.side_effect = [Exception("Processing error"), [Mock()]]
        
        processor = DocumentProcessor()
        documents = processor.process_directory("/test")
        
        captured = capsys.readouterr()
        assert "Error processing" in captured.out
        assert len(documents) == 1  # Only successful processing
    
    def test_chunk_metadata_consistency(self, sample_txt_path):
        """Test that chunk metadata is consistent"""
        processor = DocumentProcessor(chunk_size=30, chunk_overlap=5)
        documents = processor.process_document(sample_txt_path)
        
        # Check chunk IDs are sequential
        chunk_ids = [doc.metadata["chunk_id"] for doc in documents]
        assert chunk_ids == list(range(len(documents)))
        
        # Check total_chunks is consistent
        total_chunks = documents[0].metadata["total_chunks"]
        assert all(doc.metadata["total_chunks"] == total_chunks for doc in documents)
        assert total_chunks == len(documents)