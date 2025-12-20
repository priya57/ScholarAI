from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

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

# Mock Test Models
class TestGenerateRequest(BaseModel):
    subject: Optional[str] = None
    difficulty: Optional[str] = None
    num_questions: int = Field(default=10, ge=1, le=50)

class TestSubmitRequest(BaseModel):
    test_id: str
    student_id: str
    answers: List[int]
    time_taken: int

class TestResult(BaseModel):
    test_id: str
    student_id: str
    score: float
    total_questions: int
    correct_answers: int
    time_taken: int
    subject_scores: Dict
    timestamp: datetime

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

# Mobile UI Models
class MobileQueryRequest(BaseModel):
    message: str
    student_id: Optional[str] = None
    context: Optional[str] = None
    user_role: Optional[str] = Field(default="student", description="User role for personalized experience")

class FiltersResponse(BaseModel):
    document_types: List[str]
    companies: List[str]
    subjects: List[str]
    difficulties: List[str]
    years: List[str]

# User role models
class UserRole(BaseModel):
    user_id: str
    role: str = Field(..., description="Role: student, faculty, admin")
    permissions: List[str] = Field(default=[], description="Specific permissions")

class AdminUploadRequest(BaseModel):
    admin_id: str
    content_type: str = Field(..., description="Type: exam, competitive, placement, curriculum")
    target_audience: str = Field(..., description="Audience: college, school, general")
    metadata: Optional[Dict] = None