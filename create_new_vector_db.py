import json
import chromadb
import os
import time

def create_vector_db_from_processed():
    """Create vector database from already processed documents"""
    
    # Initialize ChromaDB client
    client = chromadb.PersistentClient(path="./chroma_db_new")
    
    # Create collection
    collection = client.get_or_create_collection(
        name="placement_papers",
        metadata={"description": "Placement papers and study materials"}
    )
    
    # Load processed documents
    with open('processed_data/documents.json', 'r', encoding='utf-8') as f:
        documents = json.load(f)
    
    print(f"Loading {len(documents)} documents into vector database...")
    
    # Process in batches
    batch_size = 50
    total_batches = (len(documents) + batch_size - 1) // batch_size
    
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i+batch_size]
        
        texts = [doc['content'] for doc in batch_docs]
        metadatas = [doc['metadata'] for doc in batch_docs]
        ids = [f"doc_{i+j}" for j in range(len(batch_docs))]
        
        try:
            collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            print(f"Added batch {i//batch_size + 1}/{total_batches}")
        except Exception as e:
            print(f"Error in batch {i//batch_size + 1}: {e}")
    
    print(f"Vector database created successfully!")
    print(f"Total documents: {collection.count()}")
    
    # Test search
    print("\n--- Testing Search ---")
    test_query = "valuelabs aptitude questions"
    results = collection.query(
        query_texts=[test_query],
        n_results=3
    )
    
    if results:
        print(f"Search results for: '{test_query}'")
        for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
            print(f"\n{i+1}. Company: {metadata.get('company', 'N/A')}")
            print(f"   File: {metadata.get('file_name', 'N/A')}")
            print(f"   Content: {doc[:150]}...")
    
    return collection

if __name__ == "__main__":
    create_vector_db_from_processed()