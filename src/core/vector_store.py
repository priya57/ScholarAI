from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document as LangchainDocument
from typing import List, Optional, Dict, Any
import os
import pickle

class VectorStoreManager:
    def __init__(self, database_url: str, openai_api_key: str):
        self.persist_directory = "./data"
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.index_path = os.path.join(self.persist_directory, "faiss_index")
        
        os.makedirs(self.persist_directory, exist_ok=True)
        
        if os.path.exists(self.index_path + ".faiss"):
            self.vector_store = FAISS.load_local(self.persist_directory, self.embeddings, "faiss_index")
        else:
            self.vector_store = None
    
    def add_documents(self, documents: List[LangchainDocument]) -> None:
        if not documents:
            return
            
        if self.vector_store is None:
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
        else:
            self.vector_store.add_documents(documents)
        
        self.vector_store.save_local(self.persist_directory, "faiss_index")
        print(f"Added {len(documents)} documents to vector store")
    
    def similarity_search(self, query: str, k: int = 5) -> List[LangchainDocument]:
        if self.vector_store is None:
            return []
        return self.vector_store.similarity_search(query, k=k)
    
    def similarity_search_with_filters(self, query: str, k: int = 5, filters: Optional[Dict] = None) -> List[LangchainDocument]:
        if self.vector_store is None:
            return []
        
        results = self.vector_store.similarity_search(query, k=k*2)
        
        if filters:
            filtered_results = []
            for doc in results:
                match = True
                for key, value in filters.items():
                    if doc.metadata.get(key) != value:
                        match = False
                        break
                if match:
                    filtered_results.append(doc)
                if len(filtered_results) >= k:
                    break
            return filtered_results[:k]
        
        return results[:k]
    
    def get_available_filters(self) -> Dict[str, List[str]]:
        if self.vector_store is None:
            return {}
        
        try:
            all_docs = self.vector_store.similarity_search("", k=1000)
            
            filters = {
                "document_types": list(set(doc.metadata.get("document_type") for doc in all_docs if doc.metadata.get("document_type"))),
                "companies": list(set(doc.metadata.get("company") for doc in all_docs if doc.metadata.get("company"))),
                "subjects": list(set(doc.metadata.get("subject") for doc in all_docs if doc.metadata.get("subject"))),
                "difficulties": list(set(doc.metadata.get("difficulty") for doc in all_docs if doc.metadata.get("difficulty"))),
                "years": list(set(doc.metadata.get("year") for doc in all_docs if doc.metadata.get("year")))
            }
            return filters
        except:
            return {}
    
    def get_collection_count(self) -> int:
        if self.vector_store is None:
            return 0
        try:
            return len(self.vector_store.docstore._dict)
        except:
            return 0
    
    def reset_collection(self) -> None:
        try:
            if os.path.exists(self.index_path + ".faiss"):
                os.remove(self.index_path + ".faiss")
            if os.path.exists(self.index_path + ".pkl"):
                os.remove(self.index_path + ".pkl")
            self.vector_store = None
            print("Reset vector store")
        except Exception as e:
            print(f"Error resetting: {str(e)}")