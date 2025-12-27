#!/usr/bin/env python3
"""
Setup script to install dependencies and start the ScholarAI API
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("Setting up ScholarAI dependencies...")
    
    # Essential packages for the API to work
    essential_packages = [
        "fastapi==0.104.1",
        "uvicorn==0.24.0", 
        "langchain==0.1.0",
        "langchain-openai==0.0.2",
        "langchain-community==0.0.10",
        "chromadb==0.4.18",
        "pypdf2==3.0.1",
        "python-docx==1.1.0",
        "python-multipart==0.0.6",
        "pydantic==2.5.0",
        "python-dotenv==1.0.0"
    ]
    
    print("Installing essential packages...")
    for package in essential_packages:
        print(f"Installing {package}...")
        if install_package(package):
            print(f"✓ {package} installed successfully")
        else:
            print(f"✗ Failed to install {package}")
    
    print("\nSetup complete!")
    print("\nTo start the API server, run:")
    print("python -m uvicorn src.api.main:app --reload --port 8000")
    print("\nTo start the UI server, run:")
    print("python serve_ui.py")

if __name__ == "__main__":
    main()