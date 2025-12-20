import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from typing import List, Optional, Dict, Any
import os

class VectorStoreManager:
    def __init__(self, persist_directory: str, collection_name: str, openai_api_key: str):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        
        os.makedirs(persist_directory, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        self.vector_store = Chroma(
            client=self.client,
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=persist_directory
        )
    
    def add_documents(self, documents: List[Document]) -> None:
        if not documents:
            return
        self.vector_store.add_documents(documents)
        print(f"Added {len(documents)} documents to vector store")
    
    def similarity_search_with_filters(self, query: str, k: int = 5, filters: Optional[Dict] = None) -> List[Document]:
        """Search with metadata filters"""
        if filters:
            return self.vector_store.similarity_search(query, k=k, filter=filters)
        return self.vector_store.similarity_search(query, k=k)
    
    def filter_by_document_type(self, query: str, doc_type: str, k: int = 5) -> List[Document]:
        """Filter by document type: learning_material, mock_test, placement_paper"""
        return self.similarity_search_with_filters(query, k, {"document_type": doc_type})
    
    def filter_by_company(self, query: str, company: str, k: int = 5) -> List[Document]:
        """Filter placement papers by company"""
        return self.similarity_search_with_filters(query, k, {"company": company})
    
    def filter_by_subject(self, query: str, subject: str, k: int = 5) -> List[Document]:
        """Filter by subject/topic"""
        return self.similarity_search_with_filters(query, k, {"subject": subject})
    
    def filter_by_difficulty(self, query: str, difficulty: str, k: int = 5) -> List[Document]:
        """Filter by difficulty: easy, medium, hard"""
        return self.similarity_search_with_filters(query, k, {"difficulty": difficulty})
    
    def get_available_filters(self) -> Dict[str, List[str]]:
        """Get all available filter values"""
        try:
            collection = self.client.get_collection(self.collection_name)
            all_metadata = collection.get()["metadatas"]
            
            filters = {
                "document_types": list(set(m.get("document_type") for m in all_metadata if m.get("document_type"))),
                "companies": list(set(m.get("company") for m in all_metadata if m.get("company"))),
                "subjects": list(set(m.get("subject") for m in all_metadata if m.get("subject"))),
                "difficulties": list(set(m.get("difficulty") for m in all_metadata if m.get("difficulty"))),
                "years": list(set(m.get("year") for m in all_metadata if m.get("year")))
            }
            return filters
        except:
            return {}
    
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        return self.vector_store.similarity_search(query, k=k)
    
    def similarity_search_with_score(self, query: str, k: int = 5) -> List[tuple]:
        return self.vector_store.similarity_search_with_score(query, k=k)
    
    def get_collection_count(self) -> int:
        try:
            collection = self.client.get_collection(self.collection_name)
            return collection.count()
        except:
            return 0
    
    def delete_collection(self) -> None:
        try:
            self.client.delete_collection(self.collection_name)
            print(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            print(f"Error deleting collection: {str(e)}")
    
    def reset_collection(self) -> None:
        self.delete_collection()
        self.vector_store = Chroma(
            client=self.client,
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )