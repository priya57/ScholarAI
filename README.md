# ScholarAI - Domain-Specific RAG System

A production-ready Retrieval-Augmented Generation (RAG) system designed for educational institutions to enhance student learning through domain-specific AI assistance.

## 🚀 Features

- **Document Processing**: Supports PDF, DOCX, and TXT files
- **Vector Search**: ChromaDB for efficient similarity search
- **RAG Pipeline**: OpenAI GPT integration with custom prompts
- **REST API**: FastAPI-based endpoints for integration
- **Scalable**: Docker containerization with Redis caching
- **CLI Tools**: Command-line interface for management

## 📋 Prerequisites

- Python 3.11+
- OpenAI API key
- Docker & Docker Compose (for production)
- Redis (optional, for caching)

## 🛠️ Installation

### 1. Clone and Setup

```bash
git clone <repository-url>
cd ScholarAI
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy `.env` file and update with your settings:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional (defaults provided)
API_HOST=0.0.0.0
API_PORT=8000
LLM_MODEL=gpt-3.5-turbo
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

## 🚀 Quick Start

### 1. Ingest Documents

```bash
# Using CLI
python cli.py ingest /path/to/your/documents

# Using API (after starting server)
curl -X POST "http://localhost:8000/upload" \
  -F "files=@document1.pdf" \
  -F "files=@document2.docx"
```

### 2. Start API Server

```bash
# Development
python -m uvicorn src.api.main:app --reload

# Production
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 3. Query the System

```bash
# Using CLI
python cli.py query "What are the key concepts in machine learning?"

# Using API
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the key concepts in machine learning?"}'
```

## 🐳 Docker Deployment

### Development

```bash
docker build -t scholarai .
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key scholarai
```

### Production

```bash
# Set environment variables
export OPENAI_API_KEY=your_openai_api_key

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

## 📚 API Endpoints

### Core Endpoints

- `POST /query` - Ask questions to the RAG system
- `POST /search` - Search for relevant documents
- `POST /upload` - Upload documents for processing
- `GET /health` - Health check
- `GET /stats` - System statistics

### Example Usage

```python
import requests

# Query the system
response = requests.post("http://localhost:8000/query", json={
    "question": "Explain sorting algorithms",
    "max_docs": 5
})

result = response.json()
print(result["answer"])
```

## 🔧 CLI Commands

```bash
# Ingest documents
python cli.py ingest /path/to/documents

# Query system
python cli.py query "Your question here"

# Show statistics
python cli.py stats

# Reset vector store
python cli.py reset
```

## 📊 System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Documents     │───▶│  Document       │───▶│   ChromaDB      │
│  (PDF/DOCX/TXT) │    │  Processor      │    │ (Vector Store)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌─────────────────┐             │
│   Student       │───▶│   RAG Engine    │◀────────────┘
│   Query         │    │  (LangChain)    │
└─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   OpenAI GPT    │
                       │   (Generation)  │
                       └─────────────────┘
```

## 🔒 Security Considerations

- Store API keys securely using environment variables
- Implement rate limiting for production use
- Use HTTPS in production
- Validate and sanitize all inputs
- Monitor API usage and costs

## 📈 Scaling for 40,000+ Students

### Performance Optimizations

1. **Horizontal Scaling**: Use multiple API instances behind a load balancer
2. **Caching**: Redis for frequently asked questions
3. **Database**: Consider PostgreSQL with pgvector for larger datasets
4. **CDN**: Cache static responses and documents

### Recommended Production Setup

```yaml
# docker-compose.prod.yml
services:
  scholarai-api:
    deploy:
      replicas: 4
    resources:
      limits:
        memory: 2G
        cpus: '1.0'
```

## 🛠️ Customization

### Custom Prompts

Edit `src/core/rag_engine.py` to modify the prompt template:

```python
self.prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""Your custom prompt here..."""
)
```

### Document Processing

Extend `src/core/document_processor.py` for additional file formats:

```python
def extract_text_from_pptx(self, file_path: str) -> str:
    # Your implementation
    pass
```

## 📝 Monitoring & Logging

- API logs: `logs/api.log`
- System metrics: `/stats` endpoint
- Health checks: `/health` endpoint
- Docker logs: `docker-compose logs -f`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the logs for error messages
2. Verify environment variables are set correctly
3. Ensure OpenAI API key has sufficient credits
4. Check document formats are supported (PDF, DOCX, TXT)

## 🔄 Updates & Maintenance

```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Backup vector store
cp -r data/chroma_db data/chroma_db_backup_$(date +%Y%m%d)

# Monitor system resources
docker stats
```