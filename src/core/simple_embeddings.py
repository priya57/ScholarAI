import os
from typing import List, Dict, Any
from pathlib import Path
import hashlib

class SimpleEmbeddingProcessor:
    """Simple embedding processor for text files that can be extended"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.supported_extensions = {'.txt', '.md', '.py', '.js', '.html', '.css'}
    
    def process_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Process a single file and return chunks with metadata"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if file_path.suffix.lower() not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        
        # Create chunks
        chunks = self._create_chunks(content)
        
        # Create documents with metadata
        documents = []
        for i, chunk in enumerate(chunks):
            doc = {
                'content': chunk,
                'metadata': {
                    'file_name': file_path.name,
                    'file_path': str(file_path),
                    'file_type': file_path.suffix.lower(),
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'file_size': file_path.stat().st_size,
                    'file_hash': self._get_file_hash(file_path)
                }
            }
            documents.append(doc)
        
        return documents
    
    def _create_chunks(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at sentence or paragraph boundary
            if end < len(text):
                # Look for sentence endings
                for i in range(end, max(start + self.chunk_size // 2, end - 100), -1):
                    if text[i] in '.!?\n':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - self.chunk_overlap
            if start >= len(text):
                break
        
        return chunks
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Generate hash for file content"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def process_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """Process all supported files in a directory"""
        directory = Path(directory_path)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        all_documents = []
        
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                try:
                    documents = self.process_file(str(file_path))
                    all_documents.extend(documents)
                    print(f"Processed: {file_path.name} ({len(documents)} chunks)")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
        
        return all_documents

# Example usage and test
if __name__ == "__main__":
    processor = SimpleEmbeddingProcessor()
    
    # Create a sample text file for testing
    sample_content = """
    Machine Learning Fundamentals
    
    Machine learning is a subset of artificial intelligence that focuses on algorithms 
    that can learn and make decisions from data. There are three main types of machine learning:
    
    1. Supervised Learning: Uses labeled data to train models
    2. Unsupervised Learning: Finds patterns in unlabeled data  
    3. Reinforcement Learning: Learns through interaction with environment
    
    Common algorithms include linear regression, decision trees, neural networks, 
    and support vector machines. Each has its strengths and use cases.
    """
    
    # Save sample file
    with open('sample_ml.txt', 'w') as f:
        f.write(sample_content)
    
    # Process the file
    documents = processor.process_file('sample_ml.txt')
    
    print(f"Created {len(documents)} chunks:")
    for i, doc in enumerate(documents):
        print(f"\nChunk {i+1}:")
        print(f"Content: {doc['content'][:100]}...")
        print(f"Metadata: {doc['metadata']}")