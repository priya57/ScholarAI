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

### Development Environment (5 Core Services)

```bash
# Windows
scripts\setup-dev.bat

# Linux/Mac
scripts/setup-dev.sh
```

**Available Services:**
- ScholarAI API: http://localhost:8000
- ChromaDB: http://localhost:8001
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- Adminer (DB UI): http://localhost:8080

### Production Environment (12 Services for Scale)

```bash
# Set required environment variables
export OPENAI_API_KEY=your_key
export DB_PASSWORD=secure_password
export GRAFANA_PASSWORD=admin_password

# Windows
scripts\setup-prod.bat

# Linux/Mac
scripts/setup-prod.sh
```

**Available Services:**
- ScholarAI API (Load Balanced): http://localhost
- Grafana Dashboard: http://localhost:3000
- Prometheus Metrics: http://localhost:9090
- MinIO Console: http://localhost:9001
- Qdrant Dashboard: http://localhost:6333/dashboard

## 🐳 Docker Deployment

### Development (5 Services)

```bash
# Quick setup
scripts/setup-dev.bat  # Windows
scripts/setup-dev.sh   # Linux/Mac

# Manual setup
docker-compose -f docker-compose.dev.yml up -d
```

### Production (12 Services)

```bash
# Set environment variables
export OPENAI_API_KEY=your_key
export DB_PASSWORD=secure_password
export GRAFANA_PASSWORD=admin_password

# Quick setup
scripts/setup-prod.bat  # Windows
scripts/setup-prod.sh   # Linux/Mac

# Manual setup
docker-compose -f docker-compose.prod.yml up -d

# Scale API instances
docker-compose -f docker-compose.prod.yml up -d --scale scholarai-api=5
```

### Health Monitoring

```bash
# Check all services
scripts/health-check.bat      # Windows
scripts/health-check.sh       # Linux/Mac

# Development services only
scripts/health-check.bat dev  # Windows
scripts/health-check.sh dev   # Linux/Mac
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

## 🛠️ Management Scripts

### Setup Scripts
```bash
# Development environment
scripts/setup-dev.bat    # Windows
scripts/setup-dev.sh     # Linux/Mac

# Production environment
scripts/setup-prod.bat   # Windows
scripts/setup-prod.sh    # Linux/Mac
```

### Monitoring Scripts
```bash
# Health checks
scripts/health-check.bat [dev]  # Windows
scripts/health-check.sh [dev]   # Linux/Mac

# Scaling (production only)
scripts/scale.bat 5      # Windows - scale to 5 instances
scripts/scale.sh 5       # Linux/Mac - scale to 5 instances

# Backup (production only)
scripts/backup.bat       # Windows
scripts/backup.sh        # Linux/Mac
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

### Infrastructure Costs (Monthly)

**Development Environment**
- Vector DB: Free (Qdrant/Pinecone starter)
- Hosting: $20-50/month
- Database: Free (SQLite/Supabase free tier)
- **Total: $20-50/month**

**Production Environment (40K+ students)**
- Vector DB: $70-100/month (Pinecone Standard)
- Hosting: $100-300/month (AWS/Azure/GCP)
- Database: $50-200/month (PostgreSQL)
- Caching: $30-100/month (Redis)
- Storage: $20-75/month (S3/MinIO)
- CDN: $20-100/month (CloudFlare)
- Monitoring: $50-200/month (Grafana/Prometheus)
- OpenAI API: $500-2000/month (usage-based)
- **Total: $840-3075/month**

### Scaling Strategy

**Phase 1: MVP (0-1K users)**
- ChromaDB + SQLite
- Single server deployment
- Cost: $20-50/month

**Phase 2: Growth (1K-10K users)**
- Qdrant Cloud + PostgreSQL
- Load balancer + 2 servers
- Cost: $200-500/month

**Phase 3: Scale (10K-40K+ users)**
- Pinecone + Multi-region deployment
- Auto-scaling + CDN
- Cost: $800-3000/month

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