# ScholarAI Development Setup Guide

## Development Services (5 Core Services)

1. **ScholarAI API** - Main application with hot reload
2. **Redis** - Caching and session management
3. **ChromaDB** - Vector database (lightweight)
4. **PostgreSQL** - Optional relational database
5. **Adminer** - Database management UI

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- OpenAI API key

### 1. Setup Environment
```bash
# Clone repository
git clone <repository-url>
cd ScholarAI

# Copy environment template
cp .env.dev.template .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Start Development Services
```bash
# Windows
scripts\setup-dev.bat

# Linux/Mac
scripts/setup-dev.sh

# Or manually
docker-compose -f docker-compose.dev.yml up -d
```

### 3. Verify Services
```bash
# Check API
curl http://localhost:8000/health

# Check ChromaDB
curl http://localhost:8001/api/v1/heartbeat

# Check Redis
docker exec scholarai-redis-dev redis-cli ping
```

## Available Services

| Service | URL | Purpose |
|---------|-----|---------|
| ScholarAI API | http://localhost:8000 | Main application |
| API Docs | http://localhost:8000/docs | Interactive API documentation |
| ChromaDB | http://localhost:8001 | Vector database |
| PostgreSQL | localhost:5432 | Relational database |
| Redis | localhost:6379 | Caching |
| Adminer | http://localhost:8080 | Database UI |

## Environment Configuration

### Required Variables (.env)
```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Application
ENVIRONMENT=development
DEBUG=true
API_HOST=0.0.0.0
API_PORT=8000

# LLM Settings
LLM_MODEL=gpt-3.5-turbo
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Database (SQLite by default)
DATABASE_URL=sqlite:///./scholarai.db

# Vector Database
CHROMA_HOST=localhost
CHROMA_PORT=8001

# Redis
REDIS_URL=redis://localhost:6379/0
```

## Development Workflow

### 1. Upload Documents
```bash
# Using CLI
python cli.py ingest /path/to/documents

# Using API
curl -X POST "http://localhost:8000/upload" \
  -F "file=@document.pdf"
```

### 2. Query System
```bash
# Using CLI
python cli.py query "Explain machine learning"

# Using API
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "Explain machine learning", "max_docs": 5}'
```

### 3. Monitor Services
```bash
# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Check service status
docker-compose -f docker-compose.dev.yml ps

# Monitor resources
docker stats
```

## Database Management

### PostgreSQL (Optional)
```bash
# Connect to database
docker exec -it scholarai-postgres-dev psql -U dev_user -d scholarai_dev

# Using Adminer UI
# Go to http://localhost:8080
# Server: postgres
# Username: dev_user
# Password: dev_pass
# Database: scholarai_dev
```

### ChromaDB
```bash
# List collections
curl http://localhost:8001/api/v1/collections

# Get collection info
curl http://localhost:8001/api/v1/collections/documents
```

## Troubleshooting

### Common Issues

**Services not starting:**
```bash
# Check Docker is running
docker info

# View service logs
docker-compose -f docker-compose.dev.yml logs service-name

# Restart services
docker-compose -f docker-compose.dev.yml restart
```

**API not responding:**
```bash
# Check if port is in use
netstat -an | grep 8000

# Check API logs
docker-compose -f docker-compose.dev.yml logs scholarai-api
```

**ChromaDB connection issues:**
```bash
# Check ChromaDB status
curl http://localhost:8001/api/v1/heartbeat

# Restart ChromaDB
docker-compose -f docker-compose.dev.yml restart chromadb
```

**Out of memory:**
```bash
# Check resource usage
docker stats

# Clean up unused containers/images
docker system prune -a
```

## Development Commands

### Service Management
```bash
# Start services
docker-compose -f docker-compose.dev.yml up -d

# Stop services
docker-compose -f docker-compose.dev.yml down

# Restart specific service
docker-compose -f docker-compose.dev.yml restart scholarai-api

# View logs
docker-compose -f docker-compose.dev.yml logs -f scholarai-api

# Reset all data (careful!)
docker-compose -f docker-compose.dev.yml down -v
```

### CLI Commands
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

### Testing
```bash
# Run tests
pytest

# Run specific test
pytest tests/test_api.py

# Run with coverage
pytest --cov=src tests/
```

## Resource Requirements

### Minimum
- **CPU**: 2 cores
- **RAM**: 4 GB
- **Storage**: 10 GB
- **Network**: Standard broadband

### Recommended
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Storage**: 20 GB SSD
- **Network**: High-speed internet

## Development Tips

### Hot Reload
The development setup includes hot reload - code changes are automatically reflected without restarting containers.

### Debugging
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# View detailed logs
docker-compose -f docker-compose.dev.yml logs -f --tail=100
```

### Performance
```bash
# Monitor API performance
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health

# Check database performance
docker exec scholarai-postgres-dev pg_stat_activity
```

### Data Persistence
Development data is persisted in Docker volumes:
- `redis-dev-data` - Redis cache
- `chroma-dev-data` - Vector embeddings
- `postgres-dev-data` - PostgreSQL data

## Cost Estimate

### Development Environment
- **Local hosting**: Free
- **OpenAI API**: $5-20/month (development usage)
- **Total**: $5-20/month

## Next Steps

1. **Test the setup**: Upload a document and query it
2. **Explore API docs**: Visit http://localhost:8000/docs
3. **Check logs**: Monitor application behavior
4. **Customize**: Modify prompts and configurations
5. **Scale up**: Move to production when ready

## Support

### Logs Location
- API logs: `docker-compose logs scholarai-api`
- All services: `docker-compose logs`

### Common Solutions
- **Port conflicts**: Change ports in docker-compose.dev.yml
- **Memory issues**: Increase Docker memory limit
- **API key issues**: Verify OPENAI_API_KEY in .env file