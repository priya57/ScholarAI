#!/usr/bin/env python3
"""
ScholarAI Setup Script
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def main():
    print("🚀 Setting up ScholarAI...")
    
    # Install Python dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        sys.exit(1)
    
    # Start PostgreSQL database
    if not run_command("docker-compose -f config/docker-compose.db.yml up -d", "Starting PostgreSQL database"):
        print("⚠️  Database setup failed. Make sure Docker is installed and running.")
        sys.exit(1)
    
    # Check if .env exists
    if not os.path.exists("config/.env"):
        print("⚠️  Please copy config/.env and add your OPENAI_API_KEY")
        return
    
    print("✅ ScholarAI setup completed!")
    print("\n📋 Next steps:")
    print("1. Add your OPENAI_API_KEY to config/.env")
    print("2. Run: python main.py")
    print("3. Visit: http://localhost:8000/docs")

if __name__ == "__main__":
    main()