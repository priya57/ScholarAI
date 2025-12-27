#!/usr/bin/env python3
"""
Quick start script for ScholarAI API
Handles missing dependencies gracefully
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def check_dependencies():
    """Check if essential dependencies are available"""
    missing = []
    
    try:
        import fastapi
    except ImportError:
        missing.append("fastapi")
    
    try:
        import uvicorn
    except ImportError:
        missing.append("uvicorn")
    
    try:
        import langchain
    except ImportError:
        missing.append("langchain")
    
    try:
        import chromadb
    except ImportError:
        missing.append("chromadb")
    
    if missing:
        print("Missing dependencies:")
        for dep in missing:
            print(f"  - {dep}")
        print("\nInstall with: pip install " + " ".join(missing))
        return False
    
    return True

def start_api():
    """Start the API server"""
    if not check_dependencies():
        return
    
    try:
        import uvicorn
        print("Starting ScholarAI API server...")
        print("API will be available at: http://localhost:8000")
        print("API docs at: http://localhost:8000/docs")
        print("Press Ctrl+C to stop")
        
        uvicorn.run(
            "src.api.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True
        )
    except Exception as e:
        print(f"Error starting API: {e}")
        print("\nTry installing missing dependencies:")
        print("pip install fastapi uvicorn langchain langchain-openai langchain-community chromadb")

if __name__ == "__main__":
    start_api()