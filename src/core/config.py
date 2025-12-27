from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    
    # LLM Configuration
    openai_api_key: str
    llm_model: str = "gpt-3.5-turbo"
    embedding_model: str = "text-embedding-ada-002"
    
    # Database
    database_url: str
    
    # Document Processing
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_docs_per_query: int = 5
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = "config/.env"

settings = Settings()