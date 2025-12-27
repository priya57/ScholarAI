# Manual Local Setup Guide

If the automated setup script fails, follow these manual steps:

## Step 1: Create Virtual Environment
```bash
python -m venv scholarai_env
```

## Step 2: Activate Virtual Environment
```bash
# Windows
scholarai_env\Scripts\activate

# Linux/Mac  
source scholarai_env/bin/activate
```

## Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install fastapi uvicorn pydantic pydantic-settings python-multipart python-dotenv scikit-learn numpy
```

## Step 4: Create Directories
```bash
mkdir data\uploads
mkdir data\vector_db
mkdir logs
```

## Step 5: Create .env File
Create a file named `.env` with this content:
```
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
```

## Step 6: Start the Server
```bash
python run_local.py
```

## Test the Setup
Open browser to: http://localhost:8000/docs