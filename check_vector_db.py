import json
import chromadb
import os
from pathlib import Path
from collections import defaultdict

def check_vector_db_completeness():
    """Check if all files are properly added to vector database"""
    
    # 1. Get all files that should be processed
    print("Scanning data directory for files...")
    expected_files = []
    supported_extensions = ['.pdf', '.docx', '.txt', '.rtf', '.doc', '.jpg', '.jpeg', '.png']
    
    for root, dirs, files in os.walk("data"):
        for file in files:
            if Path(file).suffix.lower() in supported_extensions:
                file_path = os.path.join(root, file)
                expected_files.append(file_path)
    
    print(f"Found {len(expected_files)} files in data directory")
    
    # 2. Check vector database
    try:
        client = chromadb.PersistentClient(path="./chroma_db")
        collection = client.get_collection("placement_papers")
        
        # Get all documents from vector DB
        all_docs = collection.get(include=['metadatas'])
        print(f"Vector database contains {len(all_docs['ids'])} chunks")
        
        # Extract unique source files from vector DB
        db_files = set()
        company_stats = defaultdict(int)
        file_type_stats = defaultdict(int)
        
        for metadata in all_docs['metadatas']:
            source = metadata.get('source', '')
            company = metadata.get('company', 'Unknown')
            file_type = metadata.get('file_type', 'unknown')
            
            if source:
                db_files.add(source)
                company_stats[company] += 1
                file_type_stats[file_type] += 1
        
        print(f"Vector database has chunks from {len(db_files)} unique files")
        
        # 3. Compare files
        expected_set = set(expected_files)
        missing_files = expected_set - db_files
        extra_files = db_files - expected_set
        
        print(f"\n=== COMPARISON RESULTS ===")
        print(f"Expected files: {len(expected_set)}")
        print(f"Files in vector DB: {len(db_files)}")
        print(f"Missing files: {len(missing_files)}")
        print(f"Extra files: {len(extra_files)}")
        
        if missing_files:
            print(f"\n=== MISSING FILES ===")
            for file in sorted(missing_files):
                print(f"  {file}")
        
        if extra_files:
            print(f"\n=== EXTRA FILES (duplicates/old paths) ===")
            for file in sorted(extra_files):
                print(f"  {file}")
        
        # 4. Show statistics
        print(f"\n=== COMPANY STATISTICS ===")
        for company, count in sorted(company_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  {company}: {count} chunks")
        
        print(f"\n=== FILE TYPE STATISTICS ===")
        for file_type, count in sorted(file_type_stats.items()):
            print(f"  {file_type}: {count} chunks")
        
        # 5. Check for specific companies
        print(f"\n=== COMPANY COVERAGE CHECK ===")
        companies_in_data = set()
        for file_path in expected_files:
            path_lower = file_path.lower()
            if 'cocubes' in path_lower:
                companies_in_data.add('Cocubes')
            elif 'mphasis' in path_lower:
                companies_in_data.add('Mphasis')
            elif 'valuelabs' in path_lower:
                companies_in_data.add('Valuelabs')
            elif 'zenq' in path_lower:
                companies_in_data.add('Zenq')
        
        companies_in_db = set(company_stats.keys()) - {'Unknown'}
        
        print(f"Companies in data folder: {sorted(companies_in_data)}")
        print(f"Companies in vector DB: {sorted(companies_in_db)}")
        
        missing_companies = companies_in_data - companies_in_db
        if missing_companies:
            print(f"Missing companies: {sorted(missing_companies)}")
        else:
            print("✅ All companies are represented in vector DB")
        
        return len(missing_files) == 0 and len(extra_files) == 0
        
    except Exception as e:
        print(f"Error accessing vector database: {e}")
        return False

if __name__ == "__main__":
    is_complete = check_vector_db_completeness()
    print(f"\n=== FINAL RESULT ===")
    if is_complete:
        print("✅ Vector database is complete and up-to-date")
    else:
        print("❌ Vector database needs updating")