import json
import os
import shutil
from pathlib import Path
from src.core.document_processor import DocumentProcessor

def clean_duplicates_and_process():
    """Remove duplicate folders and process only unique files"""
    
    # 1. Clean duplicate folders
    print("Cleaning duplicate folders...")
    duplicate_folders = [
        "data/Cocubes-20251221T133352Z-1-001",
        "data/Mphasis-20251221T133359Z-1-001", 
        "data/Valuelabs-20251221T133404Z-1-001",
        "data/ZenQ-20251221T133409Z-1-001"
    ]
    
    for folder in duplicate_folders:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"Removed: {folder}")
    
    # 2. Remove ZIP files
    print("Removing ZIP files...")
    for zip_file in Path("data").glob("*.zip"):
        zip_file.unlink()
        print(f"Removed: {zip_file}")
    
    # 3. Process only unique files
    print("Processing unique files...")
    processor = DocumentProcessor()
    
    # Get existing processed files to identify what's missing
    existing_files = set()
    if os.path.exists("processed_data/documents.json"):
        with open("processed_data/documents.json", "r", encoding="utf-8") as f:
            existing_docs = json.load(f)
            for doc in existing_docs:
                source = doc['metadata'].get('source', '')
                if not any(dup in source for dup in ['Cocubes-20251221', 'Mphasis-20251221', 'Valuelabs-20251221', 'ZenQ-20251221']):
                    existing_files.add(source)
    
    # Process all files from clean structure
    all_documents = []
    processed_count = 0
    
    for root, dirs, files in os.walk("data"):
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = Path(file).suffix.lower()
            
            if file_ext in ['.pdf', '.docx', '.txt', '.rtf', '.doc', '.jpg', '.jpeg', '.png']:
                try:
                    documents = processor.process_document(file_path)
                    all_documents.extend(documents)
                    processed_count += 1
                    print(f"Processed: {file_path} ({len(documents)} chunks)")
                except Exception as e:
                    print(f"Error: {file_path} - {e}")
    
    # Save clean processed data
    json_documents = []
    for doc in all_documents:
        json_documents.append({
            "content": doc.page_content,
            "metadata": doc.metadata
        })
    
    os.makedirs("processed_data", exist_ok=True)
    with open("processed_data/documents_clean.json", "w", encoding="utf-8") as f:
        json.dump(json_documents, f, indent=2, ensure_ascii=False)
    
    print(f"\nCleaned processing complete:")
    print(f"Files processed: {processed_count}")
    print(f"Total chunks: {len(json_documents)}")
    
    # Show breakdown
    companies = {}
    file_types = {}
    for doc in json_documents:
        company = doc['metadata'].get('company', 'Unknown')
        file_type = doc['metadata'].get('file_type', 'unknown')
        companies[company] = companies.get(company, 0) + 1
        file_types[file_type] = file_types.get(file_type, 0) + 1
    
    print("\nCompany breakdown:")
    for company, count in sorted(companies.items(), key=lambda x: x[1], reverse=True):
        print(f"  {company}: {count} chunks")
        
    print("\nFile type breakdown:")
    for file_type, count in sorted(file_types.items()):
        print(f"  {file_type}: {count} chunks")

if __name__ == "__main__":
    clean_duplicates_and_process()