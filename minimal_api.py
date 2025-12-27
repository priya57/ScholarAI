"""
Minimal API for ScholarAI - Works with basic FastAPI installation
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import json
from pathlib import Path
from typing import List, Dict, Any
import io

def extract_pdf_text(pdf_content: bytes) -> str:
    """Extract text from PDF content"""
    try:
        import PyPDF2
        pdf_file = io.BytesIO(pdf_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n\n"
        
        return text.strip()
    except ImportError:
        raise HTTPException(status_code=500, detail="PyPDF2 not installed. Run: pip install PyPDF2")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

def create_minimal_app():
    """Create a minimal FastAPI app"""
    
    app = FastAPI(
        title="ScholarAI Minimal API",
        description="Basic version of ScholarAI RAG system",
        version="0.1.0"
    )
    
    # Simple in-memory storage
    documents_store = []
    
    @app.get("/")
    async def root():
        return {"message": "ScholarAI Minimal API is running"}
    
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "version": "0.1.0",
            "documents_count": len(documents_store)
        }
    
    @app.post("/upload")
    async def upload_file(file: UploadFile = File(...)):
        """Upload and store a text or PDF file"""
        try:
            # Check file type
            if not file.filename.endswith(('.txt', '.md', '.py', '.js', '.html', '.css', '.pdf')):
                raise HTTPException(status_code=400, detail="Unsupported file type")
            
            # Read file content
            content = await file.read()
            
            # Process based on file type
            if file.filename.endswith('.pdf'):
                text_content = extract_pdf_text(content)
            else:
                text_content = content.decode('utf-8')
            
            # Simple chunking (split by paragraphs)
            chunks = [chunk.strip() for chunk in text_content.split('\n\n') if chunk.strip()]
            
            # If no paragraph breaks, split by sentences
            if len(chunks) == 1:
                import re
                sentences = re.split(r'[.!?]+', text_content)
                chunks = [s.strip() for s in sentences if s.strip()]
            
            # Store document
            doc_data = {
                "filename": file.filename,
                "chunks": chunks,
                "chunk_count": len(chunks),
                "file_type": "pdf" if file.filename.endswith('.pdf') else "text"
            }
            documents_store.append(doc_data)
            
            # Save to file
            upload_dir = Path("data/uploads")
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            with open(upload_dir / file.filename, 'wb') as f:
                f.write(content)
            
            return {
                "status": "success",
                "filename": file.filename,
                "file_type": doc_data["file_type"],
                "chunks_created": len(chunks),
                "message": f"File uploaded and processed into {len(chunks)} chunks"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/search")
    async def search_documents(request: Dict[str, Any]):
        """Simple keyword search in documents"""
        try:
            query = request.get("query", "").lower()
            k = request.get("k", 3)
            
            if not query:
                raise HTTPException(status_code=400, detail="Query is required")
            
            results = []
            
            for doc in documents_store:
                for i, chunk in enumerate(doc["chunks"]):
                    if query in chunk.lower():
                        results.append({
                            "filename": doc["filename"],
                            "chunk_index": i,
                            "content": chunk[:200] + "..." if len(chunk) > 200 else chunk,
                            "full_content": chunk
                        })
            
            # Limit results
            results = results[:k]
            
            return {
                "query": query,
                "results": results,
                "total_results": len(results)
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/documents")
    async def list_documents():
        """List all uploaded documents"""
        return {
            "documents": [
                {
                    "filename": doc["filename"],
                    "chunk_count": doc["chunk_count"]
                }
                for doc in documents_store
            ],
            "total_documents": len(documents_store)
        }
    
    @app.delete("/reset")
    async def reset_documents():
        """Clear all documents"""
        documents_store.clear()
        return {"status": "success", "message": "All documents cleared"}
    
    return app