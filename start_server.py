#!/usr/bin/env python3
"""
Simple ScholarAI Server Runner
"""

import uvicorn
from pathlib import Path

def main():
    # Create directories
    Path('data/uploads').mkdir(parents=True, exist_ok=True)
    Path('data/vector_db').mkdir(parents=True, exist_ok=True)
    Path('logs').mkdir(parents=True, exist_ok=True)
    
    print("🚀 Starting ScholarAI Server...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("⏹️  Press Ctrl+C to stop")
    
    # Start server directly
    uvicorn.run(
        "minimal_api:create_minimal_app",
        factory=True,
        host="127.0.0.1",
        port=8000,
        reload=False
    )

if __name__ == "__main__":
    main()