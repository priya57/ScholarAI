import os
import json
from src.core.document_processor import DocumentProcessor

def reprocess_with_rtf():
    """Reprocess all documents including RTF files"""
    processor = DocumentProcessor()
    
    # Process documents from data directory
    data_dir = "data"
    all_documents = []
    
    if os.path.exists(data_dir):
        documents = processor.process_directory(data_dir)
        all_documents.extend(documents)
    
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
    
    # Show file type breakdown
    file_types = {}
    for doc in json_documents:
        file_type = doc['metadata'].get('file_type', 'unknown')
        file_types[file_type] = file_types.get(file_type, 0) + 1
    
    print("\nFile type breakdown:")
    for file_type, count in file_types.items():
        print(f"  {file_type}: {count} chunks")

if __name__ == "__main__":
    reprocess_with_rtf()