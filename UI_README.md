# RAG Test UI

A minimal web interface for testing the ScholarAI RAG system functionality.

## Quick Start

1. **Start the API server:**
   ```bash
   python -m uvicorn src.api.main:app --reload --port 8000
   ```

2. **Serve the UI:**
   ```bash
   python serve_ui.py
   ```

3. **Open in browser:**
   - Go to `http://localhost:3000/rag_test_ui.html`
   - Or the script will try to open it automatically

## Features

### Query Testing
- **RAG Queries**: Full question-answering with context retrieval
- **Search Only**: Document retrieval without answer generation
- **Filtering**: Filter by document type (learning material, mock test, placement paper)
- **Configurable**: Adjust max documents returned (3, 5, or 10)

### Quick Tests
Pre-built test queries for common topics:
- Data Structures
- Sorting Algorithms  
- Interview Questions
- OOP Concepts

### System Stats
Real-time display of:
- Total documents in vector store
- Chunk size configuration
- AI model being used

## Usage

1. **Basic Query**: Type a question and click "Send Query"
2. **Document Search**: Click "Search Only" to see relevant documents without AI response
3. **Filtered Query**: Select a document type filter before querying
4. **Quick Tests**: Click any quick test button to run pre-defined queries
5. **Clear Results**: Clear the response area

## API Endpoints Used

- `POST /query` - RAG question answering
- `POST /query/filtered` - Filtered RAG queries
- `POST /search` - Document search
- `GET /stats` - System statistics

## Requirements

- ScholarAI API running on `http://localhost:8000`
- Modern web browser with JavaScript enabled
- Python 3.7+ (for serving the UI)

## Troubleshooting

- **API Connection Error**: Ensure the API server is running on port 8000
- **CORS Issues**: The API includes CORS headers for local development
- **No Results**: Check if documents are loaded in the vector store using `/stats`