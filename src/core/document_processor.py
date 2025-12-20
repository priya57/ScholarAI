import os
import re
from typing import List, Dict, Optional
from pathlib import Path
import PyPDF2
from docx import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document as LangchainDocument

class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def extract_metadata(self, file_path: str, content: str) -> Dict:
        """Extract enhanced metadata for filtering"""
        file_name = Path(file_path).name.lower()
        metadata = {
            "source": file_path,
            "file_name": Path(file_path).name,
            "file_type": Path(file_path).suffix.lower(),
        }
        
        # Detect document type
        if any(term in file_name for term in ['mock', 'test', 'exam', 'quiz']):
            metadata["document_type"] = "mock_test"
        elif any(term in file_name for term in ['placement', 'interview', 'company']):
            metadata["document_type"] = "placement_paper"
        else:
            metadata["document_type"] = "learning_material"
        
        # Extract company names for placement papers
        companies = ['google', 'microsoft', 'amazon', 'apple', 'meta', 'netflix', 'uber', 'airbnb']
        for company in companies:
            if company in file_name:
                metadata["company"] = company.title()
                break
        
        # Extract year
        year_match = re.search(r'20\d{2}', file_name)
        if year_match:
            metadata["year"] = year_match.group()
        
        # Extract subject/topic
        subjects = ['python', 'java', 'javascript', 'sql', 'algorithms', 'data structures', 'machine learning', 'ai']
        for subject in subjects:
            if subject.replace(' ', '') in file_name.replace(' ', ''):
                metadata["subject"] = subject.title()
                break
        
        # Extract difficulty
        if any(term in file_name for term in ['easy', 'beginner']):
            metadata["difficulty"] = "easy"
        elif any(term in file_name for term in ['hard', 'advanced', 'expert']):
            metadata["difficulty"] = "hard"
        else:
            metadata["difficulty"] = "medium"
        
        return metadata
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def extract_text_from_docx(self, file_path: str) -> str:
        doc = Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    
    def extract_text_from_txt(self, file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def process_document(self, file_path: str) -> List[LangchainDocument]:
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.pdf':
            text = self.extract_text_from_pdf(file_path)
        elif file_extension == '.docx':
            text = self.extract_text_from_docx(file_path)
        elif file_extension == '.txt':
            text = self.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        base_metadata = self.extract_metadata(file_path, text)
        chunks = self.text_splitter.split_text(text)
        
        documents = []
        for i, chunk in enumerate(chunks):
            metadata = base_metadata.copy()
            metadata.update({"chunk_id": i, "total_chunks": len(chunks)})
            
            doc = LangchainDocument(page_content=chunk, metadata=metadata)
            documents.append(doc)
        
        return documents
    
    def process_directory(self, directory_path: str) -> List[LangchainDocument]:
        all_documents = []
        supported_extensions = ['.pdf', '.docx', '.txt']
        
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if Path(file).suffix.lower() in supported_extensions:
                    file_path = os.path.join(root, file)
                    try:
                        documents = self.process_document(file_path)
                        all_documents.extend(documents)
                        print(f"Processed: {file_path} ({len(documents)} chunks)")
                    except Exception as e:
                        print(f"Error processing {file_path}: {str(e)}")
        
        return all_documents