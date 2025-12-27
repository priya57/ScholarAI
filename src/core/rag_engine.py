try:
    from langchain_openai import ChatOpenAI
except ImportError:
    from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from typing import Dict, List, Optional
import json
from .vector_store import VectorStoreManager

class RAGEngine:
    def __init__(self, vector_store_manager: VectorStoreManager, openai_api_key: str, model_name: str = "gpt-3.5-turbo"):
        self.vector_store_manager = vector_store_manager
        self.llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            model_name=model_name,
            temperature=0.1
        )
        
        # Custom prompt template for educational content
        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are an AI assistant helping students with their learning materials, mock tests, and placement preparation.

Context from learning materials:
{context}

Student Question: {question}

Instructions:
1. Provide accurate, educational responses based on the context
2. If the question is about a specific topic, explain concepts clearly
3. For practice questions, provide step-by-step solutions
4. If information is not in the context, clearly state that
5. Always encourage learning and provide additional study tips when relevant

Answer:"""
        )
        
        # Initialize retrieval chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store_manager.vector_store.as_retriever(
                search_kwargs={"k": 5}
            ),
            chain_type_kwargs={"prompt": self.prompt_template},
            return_source_documents=True
        )
    
    def query_with_docs(self, question: str, docs: List) -> Dict:
        """Query with pre-filtered documents"""
        try:
            if not docs:
                return {
                    "answer": "I couldn't find any relevant information in the specified documents for your question.",
                    "sources": [],
                    "confidence": "low",
                    "total_sources_found": 0
                }
            
            # Create context from documents
            context = "\n\n".join([doc.page_content for doc in docs])
            
            # Generate response
            prompt = self.prompt_template.format(context=context, question=question)
            response = self.llm.predict(prompt)
            
            # Format response with enhanced traceability
            result = {
                "answer": response,
                "sources": [],
                "confidence": "high" if len(docs) >= 3 else "medium",
                "total_sources_found": len(docs)
            }
            
            # Add detailed source information
            for doc in docs:
                source_info = {
                    "file_name": doc.metadata.get("file_name", "Unknown"),
                    "source": doc.metadata.get("source", "Unknown"),
                    "chunk_id": doc.metadata.get("chunk_id", 0),
                    "content_preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "document_type": doc.metadata.get("document_type"),
                    "company": doc.metadata.get("company"),
                    "subject": doc.metadata.get("subject"),
                    "difficulty": doc.metadata.get("difficulty"),
                    "year": doc.metadata.get("year")
                }
                result["sources"].append(source_info)
            
            return result
            
        except Exception as e:
            return {
                "answer": f"I apologize, but I encountered an error: {str(e)}",
                "sources": [],
                "confidence": "low",
                "total_sources_found": 0,
                "error": str(e)
            }

    def query(self, question: str, max_docs: int = 5) -> Dict:
        """Process a query and return response with sources"""
        try:
            # Update retriever with max_docs
            self.qa_chain.retriever.search_kwargs = {"k": max_docs}
            
            # Get response
            result = self.qa_chain({"query": question})
            
            # Enhanced response with better traceability
            response = {
                "answer": result["result"],
                "sources": [],
                "confidence": "high" if len(result["source_documents"]) >= 3 else "medium",
                "total_sources_found": len(result["source_documents"])
            }
            
            # Add detailed source information with metadata
            for doc in result["source_documents"]:
                source_info = {
                    "file_name": doc.metadata.get("file_name", "Unknown"),
                    "source": doc.metadata.get("source", "Unknown"),
                    "chunk_id": doc.metadata.get("chunk_id", 0),
                    "content_preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "document_type": doc.metadata.get("document_type"),
                    "company": doc.metadata.get("company"),
                    "subject": doc.metadata.get("subject"),
                    "difficulty": doc.metadata.get("difficulty"),
                    "year": doc.metadata.get("year")
                }
                response["sources"].append(source_info)
            
            return response
            
        except Exception as e:
            return {
                "answer": f"I apologize, but I encountered an error while processing your question: {str(e)}",
                "sources": [],
                "confidence": "low",
                "total_sources_found": 0,
                "error": str(e)
            }
    
    def get_relevant_documents(self, query: str, k: int = 5) -> List[Dict]:
        """Get relevant documents for a query"""
        docs = self.vector_store_manager.similarity_search_with_score(query, k=k)
        
        relevant_docs = []
        for doc, score in docs:
            doc_info = {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "relevance_score": float(score)
            }
            relevant_docs.append(doc_info)
        
        return relevant_docs
    
    def update_retriever_config(self, k: int = 5, score_threshold: float = 0.7):
        """Update retriever configuration"""
        self.qa_chain.retriever.search_kwargs = {
            "k": k,
            "score_threshold": score_threshold
        }