import json
import chromadb
import os
import shutil
from pathlib import Path
from src.core.document_processor import DocumentProcessor

def process_all_files():
    """Process all files in data directory"""
    processor = DocumentProcessor()
    
    # Clear existing processed data
    if os.path.exists("processed_data/documents.json"):
        print("Clearing existing processed data...")
    
    # Process all documents
    all_documents = processor.process_directory("data")
    
    print(f"Total documents processed: {len(all_documents)}")
    
    # Convert to JSON format
    json_documents = []
    for doc in all_documents:
        json_documents.append({
            "content": doc.page_content,
            "metadata": doc.metadata
        })
    
    # Save processed documents
    os.makedirs("processed_data", exist_ok=True)
    with open("processed_data/documents.json", "w", encoding="utf-8") as f:
        json.dump(json_documents, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(json_documents)} documents to processed_data/documents.json")
    
    # Show breakdown
    file_types = {}
    companies = {}
    for doc in json_documents:
        file_type = doc['metadata'].get('file_type', 'unknown')
        company = doc['metadata'].get('company', 'Unknown')
        file_types[file_type] = file_types.get(file_type, 0) + 1
        companies[company] = companies.get(company, 0) + 1
    
    print("\nFile type breakdown:")
    for file_type, count in sorted(file_types.items()):
        print(f"  {file_type}: {count} chunks")
        
    print("\nCompany breakdown:")
    for company, count in sorted(companies.items(), key=lambda x: x[1], reverse=True):
        print(f"  {company}: {count} chunks")

def create_fresh_vector_db():
    """Create fresh vector database"""
    # Clear existing vector database
    if os.path.exists("./chroma_db"):
        print("Clearing existing vector database...")
        shutil.rmtree("./chroma_db")
    
    # Initialize ChromaDB client
    client = chromadb.PersistentClient(path="./chroma_db")
    
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
    
    return collection

if __name__ == "__main__":
    print("Processing all files...")
    process_all_files()
    
    print("\nCreating vector database...")
    collection = create_fresh_vector_db()
    
    print("\nDone!")