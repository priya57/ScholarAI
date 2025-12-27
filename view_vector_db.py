import chromadb
import json

def view_vector_database():
    """View contents of the vector database"""
    try:
        client = chromadb.PersistentClient(path="./chroma_db")
        collection = client.get_collection("placement_papers")
        
        print(f"=== Vector Database Overview ===")
        print(f"Collection Name: {collection.name}")
        print(f"Total Documents: {collection.count()}")
        print(f"Collection Metadata: {collection.metadata}")
        
        # Get all documents (limited to first 10 for viewing)
        results = collection.get(limit=10, include=['documents', 'metadatas', 'ids'])
        
        print(f"\n=== Sample Documents (First 10) ===")
        for i, (doc_id, doc, metadata) in enumerate(zip(results['ids'], results['documents'], results['metadatas'])):
            print(f"\n{i+1}. ID: {doc_id}")
            print(f"   Company: {metadata.get('company', 'N/A')}")
            print(f"   Subject: {metadata.get('subject', 'N/A')}")
            print(f"   File: {metadata.get('file_name', 'N/A')}")
            print(f"   Content Preview: {doc[:150]}...")
        
        return collection
        
    except Exception as e:
        print(f"Error viewing database: {e}")
        return None

def search_interactive():
    """Interactive search function"""
    try:
        client = chromadb.PersistentClient(path="./chroma_db")
        collection = client.get_collection("placement_papers")
        
        while True:
            query = input("\nEnter search query (or 'quit' to exit): ").strip()
            if query.lower() == 'quit':
                break
                
            results = collection.query(
                query_texts=[query],
                n_results=5,
                include=['documents', 'metadatas', 'distances']
            )
            
            print(f"\n=== Search Results for: '{query}' ===")
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0], 
                results['metadatas'][0], 
                results['distances'][0]
            )):
                print(f"\n{i+1}. Similarity Score: {1-distance:.3f}")
                print(f"   Company: {metadata.get('company', 'N/A')}")
                print(f"   Subject: {metadata.get('subject', 'N/A')}")
                print(f"   Content: {doc[:200]}...")
                
    except Exception as e:
        print(f"Search error: {e}")

def get_stats():
    """Get database statistics"""
    try:
        client = chromadb.PersistentClient(path="./chroma_db")
        collection = client.get_collection("placement_papers")
        
        # Get all metadata to analyze
        all_data = collection.get(include=['metadatas'])
        
        companies = {}
        subjects = {}
        
        for metadata in all_data['metadatas']:
            company = metadata.get('company', 'Unknown')
            subject = metadata.get('subject', 'Unknown')
            
            companies[company] = companies.get(company, 0) + 1
            subjects[subject] = subjects.get(subject, 0) + 1
        
        print(f"\n=== Database Statistics ===")
        print(f"Total Documents: {collection.count()}")
        
        print(f"\nCompanies ({len(companies)}):")
        for company, count in sorted(companies.items(), key=lambda x: x[1], reverse=True):
            print(f"  {company}: {count} documents")
        
        print(f"\nSubjects ({len(subjects)}):")
        for subject, count in sorted(subjects.items(), key=lambda x: x[1], reverse=True):
            print(f"  {subject}: {count} documents")
            
    except Exception as e:
        print(f"Stats error: {e}")

if __name__ == "__main__":
    print("ChromaDB Vector Database Viewer")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. View database overview")
        print("2. Interactive search")
        print("3. Database statistics")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '1':
            view_vector_database()
        elif choice == '2':
            search_interactive()
        elif choice == '3':
            get_stats()
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")