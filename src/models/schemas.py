from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class QueryRequest(BaseModel):
    question: str = Field(..., description="Student's question")
    max_docs: int = Field(default=5, description="Maximum number of documents to retrieve")
    student_id: Optional[str] = Field(None, description="Student identifier for tracking")
    filters: Optional[Dict] = Field(None, description="Metadata filters")

class FilteredQueryRequest(BaseModel):
    question: str = Field(..., description="Student's question")
    document_type: Optional[str] = Field(None, description="Filter by: learning_material, mock_test, placement_paper")
    company: Optional[str] = Field(None, description="Filter by company name")
    subject: Optional[str] = Field(None, description="Filter by subject")
    difficulty: Optional[str] = Field(None, description="Filter by: easy, medium, hard")
    year: Optional[str] = Field(None, description="Filter by year")
    max_docs: int = Field(default=5, description="Maximum number of documents to retrieve")

class SourceInfo(BaseModel):
    file_name: str
    source: str
    chunk_id: int
    content_preview: str
    document_type: Optional[str] = None
    company: Optional[str] = None
    subject: Optional[str] = None
    difficulty: Optional[str] = None
    year: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceInfo]
    confidence: str
    total_sources_found: int
    error: Optional[str] = None

class DocumentUploadResponse(BaseModel):
    status: str
    message: str
    documents_processed: int
    chunks_created: int

class HealthResponse(BaseModel):
    status: str
    vector_store_count: int
    version: str

class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    k: int = Field(default=5, description="Number of results to return")

class SearchResult(BaseModel):
    content: str
    metadata: Dict
    relevance_score: float

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total_results: int

class FiltersResponse(BaseModel):
    document_types: List[str]
    companies: List[str]
    subjects: List[str]
    difficulties: List[str]
    years: List[str]