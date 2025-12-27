import json
import chromadb
import os
import shutil

def rebuild_vector_db():
    """Rebuild vector database with clean deduplicated data"""
    
    # Remove old database
    if os.path.exists("./chroma_db"):
        print("Removing old vector database...")
        try:
            shutil.rmtree("./chroma_db")
        except:
            print("Could not remove old DB, creating new one...")
    
    # Create new database
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection(
        name="placement_papers",
        metadata={"description": "Placement papers and study materials"}
    )
    
    # Load clean processed documents
    with open('processed_data/documents_clean.json', 'r', encoding='utf-8') as f:
        documents = json.load(f)
    
    print(f"Loading {len(documents)} unique documents into vector database...")
    
    # Add in batches
    batch_size = 50
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i+batch_size]
        
        texts = [doc['content'] for doc in batch_docs]
        metadatas = [doc['metadata'] for doc in batch_docs]
        ids = [f"doc_{i+j}" for j in range(len(batch_docs))]
        
        collection.add(documents=texts, metadatas=metadatas, ids=ids)
        print(f"Added batch {i//batch_size + 1}/{(len(documents) + batch_size - 1)//batch_size}")
    
    print(f"\nVector database rebuilt successfully!")
    print(f"Total documents: {collection.count()}")
    
    # Test search
    print("\n--- Testing Search ---")
    queries = ["valuelabs aptitude", "mphasis questions", "zenq placement"]
    
    for query in queries:
        results = collection.query(query_texts=[query], n_results=2)
        if results and results['documents'][0]:
            print(f"\n'{query}': Found {len(results['documents'][0])} results")
            print(f"  Company: {results['metadatas'][0][0].get('company', 'N/A')}")

if __name__ == "__main__":
    rebuild_vector_db()