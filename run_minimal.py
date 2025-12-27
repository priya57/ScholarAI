#!/usr/bin/env python3
"""
Minimal ScholarAI Server - Works without virtual environment
"""

import os
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = ['fastapi', 'uvicorn', 'pydantic']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for pkg in missing_packages:
            print(f"   - {pkg}")
        print("\n📦 Install them with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def create_basic_structure():
    """Create basic directory structure"""
    directories = ['data/uploads', 'data/vector_db', 'logs', 'src/api', 'src/core']
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # Create basic .env file
    if not Path('.env').exists():
        env_content = """ENVIRONMENT=local
API_HOST=127.0.0.1
API_PORT=8000
DEBUG=true
DATABASE_URL=sqlite:///data/vector_db/local.db
"""
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file")

def main():
    """Start the minimal server"""
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Create structure
    create_basic_structure()
    
    try:
        import uvicorn
        print("🚀 Starting ScholarAI Minimal Server...")
        print("📖 API Documentation: http://localhost:8000/docs")
        print("⏹️  Press Ctrl+C to stop")
        
        # Try to import the main app, fallback to minimal app
        try:
            from src.api.main import app
            print("✅ Using full ScholarAI API")
        except ImportError:
            print("⚠️  Using minimal API (some features disabled)")
            from minimal_api import create_minimal_app
            app = create_minimal_app()
        
        uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
        
    except ImportError:
        print("❌ uvicorn not installed. Run: pip install uvicorn fastapi")
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

if __name__ == "__main__":
    main()