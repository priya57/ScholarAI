from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
import tempfile
import shutil
from pathlib import Path

from ..core.config import settings
from ..core.document_processor import DocumentProcessor
from ..core.vector_store import VectorStoreManager
from ..core.rag_engine import RAGEngine
from ..models.schemas import (
    QueryRequest, QueryResponse, DocumentUploadResponse, 
    HealthResponse, SearchRequest, SearchResponse, FilteredQueryRequest, FiltersResponse
)

# Initialize FastAPI app
app = FastAPI(
    title="ScholarAI RAG API",
    description="Domain-specific RAG system for student learning",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for components
vector_store_manager = None
rag_engine = None
document_processor = None

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    global vector_store_manager, rag_engine, document_processor
    
    # Initialize document processor
    document_processor = DocumentProcessor(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap
    )
    
    # Initialize vector store
    vector_store_manager = VectorStoreManager(
        persist_directory=settings.chroma_persist_directory,
        collection_name=settings.collection_name,
        openai_api_key=settings.openai_api_key
    )
    
    # Initialize RAG engine
    rag_engine = RAGEngine(
        vector_store_manager=vector_store_manager,
        openai_api_key=settings.openai_api_key,
        model_name=settings.llm_model
    )
    
    print("ScholarAI RAG API initialized successfully!")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        vector_store_count=vector_store_manager.get_collection_count(),
        version="1.0.0"
    )

@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query the RAG system"""
    try:
        result = rag_engine.query(
            question=request.question,
            max_docs=request.max_docs
        )
        
        return QueryResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query/filtered", response_model=QueryResponse)
async def filtered_query(request: FilteredQueryRequest):
    """Query with advanced filtering capabilities"""
    try:
        # Build filters dict
        filters = {}
        if request.document_type:
            filters["document_type"] = request.document_type
        if request.company:
            filters["company"] = request.company
        if request.subject:
            filters["subject"] = request.subject
        if request.difficulty:
            filters["difficulty"] = request.difficulty
        if request.year:
            filters["year"] = request.year
        
        # Get filtered documents
        if filters:
            docs = vector_store_manager.similarity_search_with_filters(
                request.question, k=request.max_docs, filters=filters
            )
        else:
            docs = vector_store_manager.similarity_search(
                request.question, k=request.max_docs
            )
        
        # Generate response using RAG engine with filtered docs
        result = rag_engine.query_with_docs(request.question, docs)
        
        return QueryResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/filters", response_model=FiltersResponse)
async def get_available_filters():
    """Get all available filter options"""
    try:
        filters = vector_store_manager.get_available_filters()
        return FiltersResponse(**filters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
async def search_documents(request: SearchRequest):
    """Search for relevant documents"""
    try:
        results = rag_engine.get_relevant_documents(
            query=request.query,
            k=request.k
        )
        
        return SearchResponse(
            results=results,
            total_results=len(results)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search", response_model=SearchResponse)
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload and process documents"""
    try:
        total_documents = 0
        total_chunks = 0
        
        for file in files:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
                shutil.copyfileobj(file.file, tmp_file)
                tmp_path = tmp_file.name
            
            try:
                # Process document
                documents = document_processor.process_document(tmp_path)
                
                # Add to vector store
                vector_store_manager.add_documents(documents)
                
                total_documents += 1
                total_chunks += len(documents)
                
            finally:
                # Clean up temporary file
                os.unlink(tmp_path)
        
        return DocumentUploadResponse(
            status="success",
            message=f"Successfully processed {total_documents} documents",
            documents_processed=total_documents,
            chunks_created=total_chunks
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-directory")
async def upload_directory(directory_path: str, background_tasks: BackgroundTasks):
    """Process documents from a directory (background task)"""
    def process_directory():
        try:
            documents = document_processor.process_directory(directory_path)
            vector_store_manager.add_documents(documents)
            print(f"Background processing completed: {len(documents)} chunks added")
        except Exception as e:
            print(f"Background processing failed: {str(e)}")
    
    background_tasks.add_task(process_directory)
    
    return {"status": "processing", "message": "Directory processing started in background"}

@app.delete("/reset")
async def reset_vector_store():
    """Reset the vector store (delete all documents)"""
    try:
        vector_store_manager.reset_collection()
        return {"status": "success", "message": "Vector store reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    return {
        "total_documents": vector_store_manager.get_collection_count(),
        "collection_name": settings.collection_name,
        "chunk_size": settings.chunk_size,
        "model": settings.llm_model
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.api_workers,
        reload=False
    )