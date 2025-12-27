#!/usr/bin/env python3
"""
ScholarAI RAG System Manager (Simplified)
Works with existing processed data
"""

import json
import chromadb
import os
import sys
import time

class ScholarAIManager:
    def __init__(self):
        self.db_path = "./chroma_db"
        self.processed_data_path = "./processed_data/documents.json"
        
    def create_vector_db(self, force=False):
        """Create vector database from processed data"""
        client = chromadb.PersistentClient(path=self.db_path)
        
        try:
            collection = client.get_collection("placement_papers")
            if collection.count() > 0 and not force:
                print(f"✓ Vector DB exists with {collection.count()} documents")
                return collection
        except:
            pass
            
        if not os.path.exists(self.processed_data_path):
            print("❌ No processed data found. Please run PDF processing first.")
            return None
            
        print("🔄 Creating vector database...")
        collection = client.get_or_create_collection("placement_papers")
        
        with open(self.processed_data_path, 'r', encoding='utf-8') as f:
            documents = json.load(f)
            
        batch_size = 25
        total_batches = (len(documents) + batch_size - 1) // batch_size
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i+batch_size]
            texts = [doc['content'] for doc in batch]
            metadatas = [doc['metadata'] for doc in batch]
            ids = [f"doc_{i+j}" for j in range(len(batch))]
            
            try:
                collection.add(documents=texts, metadatas=metadatas, ids=ids)
                print(f"✓ Batch {i//batch_size + 1}/{total_batches}")
            except Exception as e:
                print(f"❌ Error in batch {i//batch_size + 1}: {e}")
                
        print(f"✅ Vector database created with {collection.count()} documents")
        return collection
        
    def search(self, query, n_results=5):
        """Search the vector database"""
        try:
            client = chromadb.PersistentClient(path=self.db_path)
            collection = client.get_collection("placement_papers")
            
            results = collection.query(query_texts=[query], n_results=n_results)
            
            print(f"\n🔍 Search results for: '{query}'")
            print("=" * 50)
            
            for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
                print(f"\n{i+1}. 🏢 {metadata.get('company', 'N/A')} | 📚 {metadata.get('subject', 'N/A')}")
                print(f"   📄 {metadata.get('file_name', 'N/A')}")
                print(f"   📝 {doc[:200]}...")
                
        except Exception as e:
            print(f"❌ Search failed: {e}")
            
    def stats(self):
        """Show system statistics"""
        print("\n📊 ScholarAI Statistics")
        print("=" * 30)
        
        if os.path.exists(self.processed_data_path):
            with open(self.processed_data_path, 'r') as f:
                docs = json.load(f)
            print(f"📄 Processed documents: {len(docs)}")
            
            companies = set(doc['metadata'].get('company', 'Unknown') for doc in docs)
            subjects = set(doc['metadata'].get('subject', 'Unknown') for doc in docs)
            print(f"🏢 Companies: {', '.join(sorted(companies))}")
            print(f"📚 Subjects: {', '.join(sorted(subjects))}")
        else:
            print("📄 No processed data found")
            
        try:
            client = chromadb.PersistentClient(path=self.db_path)
            collection = client.get_collection("placement_papers")
            print(f"🔍 Vector DB documents: {collection.count()}")
        except:
            print("🔍 Vector DB: Not created")
            
    def reset(self):
        """Reset vector database"""
        import shutil
        if os.path.exists(self.db_path):
            shutil.rmtree(self.db_path)
        print("🗑️ Vector database reset")

def main():
    manager = ScholarAIManager()
    
    if len(sys.argv) < 2:
        print("""
🎓 ScholarAI RAG System Manager

Usage:
  python rag_simple.py <command> [options]

Commands:
  vectordb        - Create vector database from processed data
  search <query>  - Search the database
  stats           - Show statistics
  reset           - Reset vector database
  
Options:
  --force         - Force recreation even if exists
        """)
        return
        
    command = sys.argv[1]
    force = "--force" in sys.argv
    
    start_time = time.time()
    
    if command == "vectordb":
        manager.create_vector_db(force)
    elif command == "search":
        if len(sys.argv) < 3:
            print("❌ Please provide a search query")
            return
        query = " ".join(sys.argv[2:])
        manager.search(query)
    elif command == "stats":
        manager.stats()
    elif command == "reset":
        manager.reset()
    else:
        print(f"❌ Unknown command: {command}")
        
    elapsed = time.time() - start_time
    print(f"\n⏱️ Completed in {elapsed:.1f}s")

if __name__ == "__main__":
    main()