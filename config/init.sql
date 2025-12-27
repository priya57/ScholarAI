-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create index for better performance (will be created after documents are added)
-- CREATE INDEX CONCURRENTLY documents_embedding_idx ON documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);