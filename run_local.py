#!/usr/bin/env python3
"""
Local Development Server for ScholarAI
Runs without Docker or external services
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """Start the local development server"""
    
    # Create necessary directories
    Path('data/uploads').mkdir(parents=True, exist_ok=True)
    Path('data/vector_db').mkdir(parents=True, exist_ok=True)
    Path('logs').mkdir(parents=True, exist_ok=True)
    
    # Check if .env file exists
    if not Path('.env').exists():
        print("❌ .env file not found!")
        print("Creating basic .env file...")
        
        env_content = """ENVIRONMENT=local
API_HOST=127.0.0.1
API_PORT=8000
DEBUG=true
DATABASE_URL=sqlite:///data/vector_db/local.db
CHUNK_SIZE=500
CHUNK_OVERLAP=50
UPLOAD_DIR=data/uploads
LOG_LEVEL=DEBUG
LOG_FILE=logs/scholarai.log
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file")
    
    print("🚀 Starting ScholarAI Local Development Server...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("⏹️  Press Ctrl+C to stop")
    print()
    
    # Start the server
    try:
        uvicorn.run(
            "src.api.main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

if __name__ == "__main__":
    main()