import json
import sqlite3
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class SimpleVectorStore:
    """Simple vector store using TF-IDF for text similarity without OpenAI API"""
    
    def __init__(self, db_path: str = "simple_vectors.db"):
        self.db_path = db_path
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.documents = []
        self.vectors = None
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                metadata TEXT NOT NULL,
                vector_index INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Load existing documents
        self._load_documents()
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to the vector store"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for doc in documents:
            cursor.execute('''
                INSERT INTO documents (content, metadata, vector_index)
                VALUES (?, ?, ?)
            ''', (
                doc['content'],
                json.dumps(doc['metadata']),
                len(self.documents)
            ))
            
            self.documents.append(doc)
        
        conn.commit()
        conn.close()
        
        # Rebuild vectors
        self._rebuild_vectors()
        print(f"Added {len(documents)} documents. Total: {len(self.documents)}")
    
    def _load_documents(self):
        """Load documents from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT content, metadata FROM documents ORDER BY id')
        rows = cursor.fetchall()
        
        self.documents = []
        for content, metadata_json in rows:
            doc = {
                'content': content,
                'metadata': json.loads(metadata_json)
            }
            self.documents.append(doc)
        
        conn.close()
        
        if self.documents:
            self._rebuild_vectors()
    
    def _rebuild_vectors(self):
        """Rebuild TF-IDF vectors for all documents"""
        if not self.documents:
            return
        
        texts = [doc['content'] for doc in self.documents]
        self.vectors = self.vectorizer.fit_transform(texts)
        print(f"Built vectors for {len(self.documents)} documents")
    
    def similarity_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        if not self.documents or self.vectors is None:
            return []
        
        # Transform query to vector
        query_vector = self.vectorizer.transform([query])
        
        # Calculate similarities
        similarities = cosine_similarity(query_vector, self.vectors).flatten()
        
        # Get top k results
        top_indices = np.argsort(similarities)[::-1][:k]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0:  # Only return relevant results
                result = {
                    'content': self.documents[idx]['content'],
                    'metadata': self.documents[idx]['metadata'],
                    'similarity_score': float(similarities[idx])
                }
                results.append(result)
        
        return results
    
    def get_document_count(self) -> int:
        """Get total number of documents"""
        return len(self.documents)
    
    def reset(self):
        """Clear all documents"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM documents')
        conn.commit()
        conn.close()
        
        self.documents = []
        self.vectors = None
        print("Vector store reset")

# Example usage
if __name__ == "__main__":
    from simple_embeddings import SimpleEmbeddingProcessor
    
    # Initialize components
    processor = SimpleEmbeddingProcessor()
    vector_store = SimpleVectorStore()
    
    # Create sample documents
    sample_files = {
        'ml_basics.txt': """
        Machine Learning is a branch of artificial intelligence that uses algorithms 
        to learn patterns from data. Common types include supervised learning, 
        unsupervised learning, and reinforcement learning.
        """,
        'python_intro.txt': """
        Python is a high-level programming language known for its simplicity and readability.
        It's widely used in data science, web development, and machine learning applications.
        Popular libraries include NumPy, Pandas, and Scikit-learn.
        """,
        'data_science.txt': """
        Data Science combines statistics, programming, and domain expertise to extract 
        insights from data. The process typically involves data collection, cleaning, 
        analysis, and visualization to make data-driven decisions.
        """
    }
    
    # Create and process sample files
    for filename, content in sample_files.items():
        with open(filename, 'w') as f:
            f.write(content)
        
        documents = processor.process_file(filename)
        vector_store.add_documents(documents)
    
    # Test similarity search
    print("\n=== Testing Similarity Search ===")
    
    queries = [
        "What is machine learning?",
        "Python programming language",
        "data analysis and statistics"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        results = vector_store.similarity_search(query, k=2)
        
        for i, result in enumerate(results):
            print(f"  Result {i+1} (score: {result['similarity_score']:.3f}):")
            print(f"    File: {result['metadata']['file_name']}")
            print(f"    Content: {result['content'][:100]}...")
    
    print(f"\nTotal documents in store: {vector_store.get_document_count()}")
    
    # Clean up sample files
    for filename in sample_files.keys():
        Path(filename).unlink(missing_ok=True)