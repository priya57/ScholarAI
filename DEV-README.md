# ScholarAI Development Quick Start

## 🚀 Get Started in 3 Steps

### 1. Setup
```bash
git clone <repository-url>
cd ScholarAI
cp .env.dev.template .env
# Add your OPENAI_API_KEY to .env
```

### 2. Start Services
```bash
# Windows
scripts\setup-dev.bat

# Linux/Mac  
scripts/setup-dev.sh
```

### 3. Test
```bash
# Upload a document
python cli.py ingest /path/to/document.pdf

# Ask a question
python cli.py query "Explain the main concepts"
```

## 📋 Development Services

| Service | URL | Purpose |
|---------|-----|---------|
| API | http://localhost:8000 | Main application |
| Docs | http://localhost:8000/docs | API documentation |
| ChromaDB | http://localhost:8001 | Vector database |
| Adminer | http://localhost:8080 | Database UI |

## 🔧 Common Commands

```bash
# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker-compose.dev.yml down

# Reset data
docker-compose -f docker-compose.dev.yml down -v

# Check health
curl http://localhost:8000/health
```

## 💡 Requirements

- Docker & Docker Compose
- Python 3.11+
- OpenAI API key
- 4GB RAM, 2 CPU cores

## 📖 Full Documentation

- [Complete Development Guide](docs/development-guide.md)
- [Full Deployment Guide](docs/deployment-guide.md)