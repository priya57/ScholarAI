#!/usr/bin/env python3
"""
ScholarAI Local Setup Script
Sets up the entire development environment without Docker
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

class LocalSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_name = "scholarai_env"
        self.is_windows = platform.system() == "Windows"
        
    def run_command(self, command, check=True):
        """Run a command and return the result"""
        try:
            if isinstance(command, list):
                result = subprocess.run(command, check=check, 
                                      capture_output=True, text=True)
            else:
                result = subprocess.run(command, shell=True, check=check, 
                                      capture_output=True, text=True)
            return result
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed: {e}")
            if e.stdout:
                print(f"stdout: {e.stdout}")
            if e.stderr:
                print(f"stderr: {e.stderr}")
            return None
    
    def check_python(self):
        """Check if Python is installed"""
        print("🔍 Checking Python installation...")
        try:
            result = subprocess.run([sys.executable, "--version"], 
                                  capture_output=True, text=True, check=True)
            version = result.stdout.strip()
            print(f"✅ Found {version}")
            
            # Check if version is 3.8+
            version_parts = version.split()[1].split('.')
            major, minor = int(version_parts[0]), int(version_parts[1])
            
            if major >= 3 and minor >= 8:
                return True
            else:
                print(f"❌ Python 3.8+ required, found {version}")
                return False
        except Exception as e:
            print(f"❌ Python not found or error: {e}")
            print("Please install Python 3.8+ from python.org")
            return False
    
    def create_virtual_environment(self):
        """Create virtual environment"""
        print("📦 Creating virtual environment...")
        
        venv_path = self.project_root / self.venv_name
        if venv_path.exists():
            print("✅ Virtual environment already exists")
            return True
        
        try:
            result = subprocess.run([sys.executable, "-m", "venv", str(venv_path)], 
                                  capture_output=True, text=True, check=True)
            print("✅ Virtual environment created")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            if e.stderr:
                print(f"Error: {e.stderr}")
            return False
    
    def get_pip_command(self):
        """Get the pip command for the virtual environment"""
        if self.is_windows:
            return str(self.project_root / self.venv_name / "Scripts" / "pip.exe")
        else:
            return str(self.project_root / self.venv_name / "bin" / "pip")
    
    def get_python_command(self):
        """Get the python command for the virtual environment"""
        if self.is_windows:
            return str(self.project_root / self.venv_name / "Scripts" / "python.exe")
        else:
            return str(self.project_root / self.venv_name / "bin" / "python")
    
    def install_dependencies(self):
        """Install Python dependencies"""
        print("📚 Installing dependencies...")
        
        pip_cmd = self.get_pip_command()
        
        # Check if pip exists
        if not Path(pip_cmd).exists():
            print(f"❌ Pip not found at {pip_cmd}")
            return False
        
        # Upgrade pip first
        try:
            subprocess.run([pip_cmd, "install", "--upgrade", "pip"], 
                         capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError:
            print("⚠️  Failed to upgrade pip, continuing...")
        
        # Install requirements
        requirements_file = self.project_root / "requirements-local.txt"
        if not requirements_file.exists():
            print("❌ requirements-local.txt not found")
            return False
        
        try:
            result = subprocess.run([pip_cmd, "install", "-r", str(requirements_file)], 
                                  capture_output=True, text=True, check=True)
            print("✅ Dependencies installed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            if e.stderr:
                print(f"Error: {e.stderr}")
            return False
    
    def create_directories(self):
        """Create necessary directories"""
        print("📁 Creating directories...")
        
        directories = [
            "data/uploads",
            "data/vector_db", 
            "logs",
            "config"
        ]
        
        for dir_path in directories:
            full_path = self.project_root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
        
        print("✅ Directories created")
        return True
    
    def setup_environment_file(self):
        """Setup environment configuration file"""
        print("📝 Setting up environment file...")
        
        env_file = self.project_root / ".env"
        template_file = self.project_root / ".env.local.template"
        
        if env_file.exists():
            print("✅ .env file already exists")
            return True
        
        if template_file.exists():
            # Copy template to .env
            with open(template_file, 'r') as src, open(env_file, 'w') as dst:
                dst.write(src.read())
            print("✅ Created .env file from template")
        else:
            # Create basic .env file
            env_content = """# Local Development Environment
ENVIRONMENT=local
API_HOST=127.0.0.1
API_PORT=8000
DEBUG=true
DATABASE_URL=sqlite:///data/vector_db/local.db
CHUNK_SIZE=500
CHUNK_OVERLAP=50
UPLOAD_DIR=data/uploads
LOG_LEVEL=DEBUG
LOG_FILE=logs/scholarai.log

# Optional - Add your OpenAI API key here
# OPENAI_API_KEY=your_key_here
"""
            with open(env_file, 'w') as f:
                f.write(env_content)
            print("✅ Created basic .env file")
        
        return True
    
    def initialize_database(self):
        """Initialize local database"""
        print("🗄️ Initializing local database...")
        
        python_cmd = self.get_python_command()
        init_script = '''
import sys
sys.path.insert(0, "src")
from core.simple_vector_store import SimpleVectorStore
store = SimpleVectorStore("data/vector_db/local.db")
print("Local database initialized successfully")
'''
        
        result = self.run_command([python_cmd, "-c", init_script])
        if result and result.returncode == 0:
            print("✅ Database initialized")
            return True
        else:
            print("⚠️  Database initialization skipped (will be created on first run)")
            return True
    
    def create_run_script(self):
        """Create run script for easy startup"""
        print("🚀 Creating run script...")
        
        if self.is_windows:
            script_content = f'''@echo off
echo Starting ScholarAI Local Development Server...
call {self.venv_name}\\Scripts\\activate.bat
python run_local.py
pause
'''
            script_path = self.project_root / "start_local.bat"
        else:
            script_content = f'''#!/bin/bash
echo "Starting ScholarAI Local Development Server..."
source {self.venv_name}/bin/activate
python run_local.py
'''
            script_path = self.project_root / "start_local.sh"
        
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        if not self.is_windows:
            os.chmod(script_path, 0o755)
        
        print(f"✅ Created {script_path.name}")
        return True
    
    def run_setup(self):
        """Run the complete setup process"""
        print("🚀 ScholarAI Local Setup Starting...")
        print("=" * 50)
        
        steps = [
            ("Checking Python", self.check_python),
            ("Creating virtual environment", self.create_virtual_environment),
            ("Installing dependencies", self.install_dependencies),
            ("Creating directories", self.create_directories),
            ("Setting up environment", self.setup_environment_file),
            ("Initializing database", self.initialize_database),
            ("Creating run script", self.create_run_script)
        ]
        
        for step_name, step_func in steps:
            if not step_func():
                print(f"\n❌ Setup failed at: {step_name}")
                return False
        
        print("\n" + "=" * 50)
        print("🎉 ScholarAI Local Setup Complete!")
        print("\n📋 Next Steps:")
        print("   1. Add your OpenAI API key to .env file (optional)")
        print("   2. Start the server:")
        
        if self.is_windows:
            print("      start_local.bat")
        else:
            print("      ./start_local.sh")
        
        print("\n📖 Once running:")
        print("   • API: http://localhost:8000")
        print("   • Docs: http://localhost:8000/docs")
        print("   • Health: http://localhost:8000/health")
        
        return True

def main():
    """Main setup function"""
    setup = LocalSetup()
    success = setup.run_setup()
    
    if not success:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)
    
    print("\n✅ Setup completed successfully!")

if __name__ == "__main__":
    main()