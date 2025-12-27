# ScholarAI Development Deployment Plan (No Docker)

## Local Development Setup

### Prerequisites
- ✅ Python 3.8+ (you have 3.12.3)
- ✅ Git
- ✅ OpenAI API key (optional for basic features)

### Architecture Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Local Files   │───▶│  FastAPI Server │───▶│   SQLite DB     │
│  (txt, md, py)  │    │  (Port 8000)    │    │ (Vector Store)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   OpenAI API    │
                       │  (Optional)     │
                       └─────────────────┘
```

## Step-by-Step Deployment

### 1. Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements-local.txt

# Verify installation
python --version
pip list
```

### 2. Project Structure
```
ScholarAI/
├── venv/                    # Virtual environment
├── src/
│   ├── api/
│   │   └── main.py         # FastAPI application
│   └── core/
│       ├── simple_embeddings.py
│       └── simple_vector_store.py
├── data/
│   ├── uploads/            # Uploaded files
│   └── vector_db/          # SQLite database
├── logs/                   # Application logs
├── .env                    # Environment variables
├── requirements-local.txt  # Dependencies
├── run_minimal.py         # Server runner
└── minimal_api.py         # Minimal API implementation
```

### 3. Configuration
```bash
# Create .env file
ENVIRONMENT=local
API_HOST=127.0.0.1
API_PORT=8000
DEBUG=true
DATABASE_URL=sqlite:///data/vector_db/local.db
CHUNK_SIZE=500
CHUNK_OVERLAP=50
UPLOAD_DIR=data/uploads
LOG_LEVEL=DEBUG

# Optional - Add when ready
# OPENAI_API_KEY=your_key_here
```

### 4. Start Development Server
```bash
# Activate virtual environment (if not active)
venv\Scripts\activate

# Start the server
python run_minimal.py

# Server will be available at:
# - API: http://localhost:8000
# - Docs: http://localhost:8000/docs
# - Health: http://localhost:8000/health
```

## Development Features

### Available Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Welcome message |
| `/health` | GET | Health check |
| `/upload` | POST | Upload text files |
| `/search` | POST | Search documents |
| `/query` | POST | Query with AI (needs OpenAI) |
| `/documents` | GET | List uploaded files |
| `/reset` | DELETE | Clear all documents |

### File Support
- ✅ Text files (.txt, .md)
- ✅ Code files (.py, .js, .html, .css)
- ✅ Basic chunking and search
- ⚠️ PDF support (requires PyPDF2)

### Testing the Setup
```bash
# 1. Check health
curl http://localhost:8000/health

# 2. Create test file
echo "Machine learning is a subset of AI" > test.txt

# 3. Upload file
curl -X POST "http://localhost:8000/upload" -F "file=@test.txt"

# 4. Search documents
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "k": 3}'
```

## Development Workflow

### Daily Development
```bash
# 1. Activate environment
venv\Scripts\activate

# 2. Start server
python run_minimal.py

# 3. Make changes to code
# 4. Server auto-reloads (uvicorn --reload)

# 5. Test changes
curl http://localhost:8000/health
```

### Adding New Features
1. **Modify** `minimal_api.py` for new endpoints
2. **Update** `requirements-local.txt` for new dependencies
3. **Test** using FastAPI docs at `/docs`
4. **Commit** changes to Git

### Database Management
```bash
# View database
sqlite3 data/vector_db/local.db
.tables
.schema
SELECT * FROM documents LIMIT 5;

# Reset database
curl -X DELETE http://localhost:8000/reset
```

## Resource Requirements

### Minimum System Requirements
- **CPU**: 2 cores
- **RAM**: 2 GB
- **Storage**: 5 GB
- **Network**: Basic internet (for OpenAI API)

### Recommended for Development
- **CPU**: 4 cores
- **RAM**: 4 GB
- **Storage**: 10 GB SSD
- **Network**: High-speed internet

## Cost Analysis

### Development Costs (Monthly)
- **Hosting**: $0 (local development)
- **Database**: $0 (SQLite)
- **Vector Store**: $0 (local TF-IDF)
- **OpenAI API**: $5-20 (development usage)
- **Total**: $5-20/month

### Scaling Path
1. **Local Development** → Current setup
2. **Cloud Development** → Deploy to Heroku/Railway ($5-10/month)
3. **Staging Environment** → Add PostgreSQL + Redis ($20-50/month)
4. **Production** → Full infrastructure ($200-500/month)

## Troubleshooting

### Common Issues
```bash
# Virtual environment not activated
# Solution: venv\Scripts\activate

# Port already in use
# Solution: Change port in .env or kill process
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Import errors
# Solution: Reinstall dependencies
pip install -r requirements-local.txt

# Database locked
# Solution: Restart server or delete database file
```

### Performance Optimization
- Use SSD for faster file I/O
- Increase chunk size for larger documents
- Enable caching for repeated queries
- Monitor memory usage with Task Manager

## Next Steps

### Phase 1: Basic Setup ✅
- [x] Local environment
- [x] Basic API endpoints
- [x] File upload and search

### Phase 2: Enhanced Features
- [ ] Add OpenAI integration
- [ ] Improve chunking algorithm
- [ ] Add user authentication
- [ ] Implement caching

### Phase 3: Production Ready
- [ ] Deploy to cloud platform
- [ ] Add proper database
- [ ] Implement monitoring
- [ ] Add CI/CD pipeline

## Deployment Commands Summary

```bash
# Complete setup in one go
python -m venv venv
venv\Scripts\activate
pip install -r requirements-local.txt
mkdir data\uploads data\vector_db logs
echo ENVIRONMENT=local > .env
python run_minimal.py
```

This gives you a fully functional development environment without Docker!