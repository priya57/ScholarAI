#!/usr/bin/env python3
"""
Example usage of ScholarAI filtering capabilities
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_basic_query():
    """Test basic query functionality"""
    response = requests.post(f"{BASE_URL}/query", json={
        "question": "Explain sorting algorithms",
        "max_docs": 5
    })
    print("Basic Query Response:")
    print(json.dumps(response.json(), indent=2))

def test_filtered_queries():
    """Test filtered query capabilities"""
    
    # Query only placement papers
    print("\n=== Placement Papers Only ===")
    response = requests.post(f"{BASE_URL}/query/filtered", json={
        "question": "What are common interview questions?",
        "document_type": "placement_paper",
        "max_docs": 3
    })
    print(json.dumps(response.json(), indent=2))
    
    # Query by company
    print("\n=== Google Placement Papers ===")
    response = requests.post(f"{BASE_URL}/query/filtered", json={
        "question": "Google interview questions",
        "company": "Google",
        "max_docs": 3
    })
    print(json.dumps(response.json(), indent=2))
    
    # Query by difficulty
    print("\n=== Easy Level Questions ===")
    response = requests.post(f"{BASE_URL}/query/filtered", json={
        "question": "Basic programming concepts",
        "difficulty": "easy",
        "max_docs": 3
    })
    print(json.dumps(response.json(), indent=2))

def get_available_filters():
    """Get all available filter options"""
    response = requests.get(f"{BASE_URL}/filters")
    print("\n=== Available Filters ===")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    print("ScholarAI Filtering Demo")
    print("=" * 50)
    
    try:
        get_available_filters()
        test_basic_query()
        test_filtered_queries()
    except requests.exceptions.ConnectionError:
        print("Error: Make sure the API server is running on http://localhost:8000")
        print("Start it with: python -m uvicorn src.api.main:app --reload")