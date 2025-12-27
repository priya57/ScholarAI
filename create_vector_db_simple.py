import json
import chromadb
import os
from pathlib import Path
from src.core.document_processor import DocumentProcessor

def reprocess_documents_with_rtf():
    """Reprocess all documents including RTF files"""
    processor = DocumentProcessor()
    
    # Process documents from data directory
    data_dir = "data"
    all_documents = []
    processed_files = set()
    
    if os.path.exists(data_dir):
        print(f"Scanning {data_dir} for documents...")
        
        # Get all supported files first to avoid duplicates
        supported_extensions = ['.pdf', '.docx', '.txt', '.rtf', '.doc', '.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        
        for root, dirs, files in os.walk(data_dir):
            for file in files:
                if Path(file).suffix.lower() in supported_extensions:
                    file_path = os.path.join(root, file)
                    
                    # Skip if already processed (avoid duplicates from extracted folders)
                    relative_path = os.path.relpath(file_path, data_dir)
                    if relative_path in processed_files:
                        print(f"Skipping duplicate: {file_path}")
                        continue
                    
                    processed_files.add(relative_path)
                    
                    try:
                        documents = processor.process_document(file_path)
                        all_documents.extend(documents)
                        print(f"Processed: {file_path} ({len(documents)} chunks)")
                    except Exception as e:
                        print(f"Error processing {file_path}: {str(e)}")
    
    print(f"Total documents processed: {len(all_documents)}")
    print(f"Total unique files processed: {len(processed_files)}")
    
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
    
    # Show file type breakdown
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
    
    return json_documents

def create_vector_database_simple(reprocess=False):
    # Reprocess documents if requested
    if reprocess:
        print("Reprocessing documents including RTF files...")
        reprocess_documents_with_rtf()
        
        # Clear existing vector database to avoid duplicates
        print("Clearing existing vector database...")
        import shutil
        if os.path.exists("./chroma_db"):
            shutil.rmtree("./chroma_db")
    
    # Initialize ChromaDB client with local embeddings
    client = chromadb.PersistentClient(path="./chroma_db")
    
    # Check if collection already exists and has data (only if not reprocessing)
    if not reprocess:
        try:
            collection = client.get_collection("placement_papers")
            existing_count = collection.count()
            if existing_count > 0:
                print(f"Vector database already exists with {existing_count} documents")
                return collection
        except:
            pass
    
    # Create collection with default embedding function (no download needed)
    collection = client.get_or_create_collection(
        name="placement_papers",
        metadata={"description": "Placement papers and study materials"}
    )
    
    # Load processed documents
    with open('processed_data/documents.json', 'r', encoding='utf-8') as f:
        documents = json.load(f)
    
    print(f"Loading {len(documents)} documents into vector database...")
    
    # Process in smaller batches to avoid timeout
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
            continue
    
    print(f"Vector database created successfully!")
    print(f"Total documents: {collection.count()}")
    
    return collection

def search_documents_simple(query, n_results=5):
    """Search documents using the vector database"""
    try:
        client = chromadb.PersistentClient(path="./chroma_db")
        collection = client.get_collection("placement_papers")
        
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        return results
    except Exception as e:
        print(f"Search error: {e}")
        return None

if __name__ == "__main__":
    import sys
    
    # Check if reprocess flag is provided
    reprocess = len(sys.argv) > 1 and sys.argv[1] == "--reprocess"
    
    # Create vector database
    collection = create_vector_database_simple(reprocess=reprocess)
    
    # Test search
    print("\n--- Testing Search ---")
    test_query = "quantitative aptitude questions"
    results = search_documents_simple(test_query)
    
    if results:
        print(f"Search results for: '{test_query}'")
        for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
            print(f"\n{i+1}. Company: {metadata.get('company', 'N/A')}")
            print(f"   Subject: {metadata.get('subject', 'N/A')}")
            print(f"   Content: {doc[:200]}...")
    else:
        print("Search failed")