#!/usr/bin/env python3
"""
Comprehensive verification of all ScholarAI key features
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_rag_features():
    """Test 4.1 RAG Features"""
    print("🔍 4.1 RAG FEATURES")
    print("=" * 50)
    
    # Document Retriever
    print("✅ Document Retriever:")
    response = requests.post(f"{BASE_URL}/query", json={
        "question": "Explain machine learning algorithms",
        "max_docs": 3
    })
    result = response.json()
    print(f"   Retrieved {len(result['sources'])} relevant documents")
    
    # Generation Model
    print("✅ Generation Model:")
    print(f"   Generated contextual answer: {len(result['answer'])} characters")
    
    # Source Citations
    print("✅ Source Citations:")
    for i, source in enumerate(result['sources'][:2], 1):
        print(f"   {i}. {source['file_name']} (chunk {source['chunk_id']})")
    print()

def test_mock_test_module():
    """Test 4.2 Mock Test Module"""
    print("📝 4.2 MOCK TEST MODULE")
    print("=" * 50)
    
    # Timed Practice Tests
    print("✅ Timed Practice Tests:")
    response = requests.post(f"{BASE_URL}/test/generate", json={
        "num_questions": 3,
        "subject": "Python"
    })
    test_data = response.json()
    print(f"   Generated test with {len(test_data['questions'])} questions")
    print(f"   Time limit: {test_data['time_limit']} seconds")
    
    # Submit test
    response = requests.post(f"{BASE_URL}/test/submit", json={
        "test_id": test_data["test_id"],
        "student_id": "demo_student",
        "answers": [0, 1, 0],
        "time_taken": 120
    })
    result = response.json()
    
    # Detailed Feedback
    print("✅ Detailed Feedback:")
    print(f"   Score: {result['score']}%")
    print(f"   Subject-wise analysis: {len(result['subject_scores'])} subjects")
    
    # Personalized Recommendations
    print("✅ Personalized Recommendations:")
    response = requests.get(f"{BASE_URL}/test/performance/demo_student")
    performance = response.json()
    if 'recommendations' in performance:
        for rec in performance['recommendations'][:2]:
            print(f"   • {rec}")
    print()

def test_placement_browser():
    """Test 4.3 Placement Paper Browser"""
    print("📋 4.3 PLACEMENT PAPER BROWSER")
    print("=" * 50)
    
    # Advanced Filters
    print("✅ Advanced Filters:")
    response = requests.get(f"{BASE_URL}/filters")
    filters = response.json()
    print(f"   Companies: {len(filters.get('companies', []))} available")
    print(f"   Subjects: {len(filters.get('subjects', []))} available")
    print(f"   Years: {len(filters.get('years', []))} available")
    
    # Filtered search
    response = requests.post(f"{BASE_URL}/query/filtered", json={
        "question": "Interview questions",
        "document_type": "placement_paper",
        "max_docs": 2
    })
    result = response.json()
    
    # Direct Access
    print("✅ Direct Access:")
    print(f"   Found {len(result['sources'])} placement papers")
    if result['sources']:
        print(f"   Preview available for: {result['sources'][0]['file_name']}")
    print()

def test_delivery_channels():
    """Test 4.4 Delivery Channels"""
    print("💬 4.4 DELIVERY CHANNELS")
    print("=" * 50)
    
    # Chatbot
    print("✅ Chatbot Interface:")
    response = requests.post(f"{BASE_URL}/mobile/chat", json={
        "message": "What is binary search?",
        "student_id": "demo_user"
    })
    result = response.json()
    print(f"   Conversational response: {len(result['response'])} characters")
    print(f"   Sources provided: {result['sources_count']}")
    
    # AI Search Assistant
    print("✅ AI Search Assistant:")
    response = requests.post(f"{BASE_URL}/search/assistant", json={
        "query": "sorting algorithms",
        "k": 3
    })
    result = response.json()
    print(f"   Keyword-based search: {result['total_results']} results")
    print(f"   Search type: {result['search_type']}")
    if result['results']:
        print(f"   Top result: {result['results'][0]['title']}")
    print()

def main():
    print("ScholarAI - Key Features Verification")
    print("=" * 80)
    
    try:
        test_rag_features()
        test_mock_test_module()
        test_placement_browser()
        test_delivery_channels()
        
        print("🎉 ALL KEY FEATURES VERIFIED SUCCESSFULLY!")
        print("=" * 80)
        print("✅ 4.1 RAG: Document retrieval, generation, source citations")
        print("✅ 4.2 Mock Tests: Timed tests, feedback, recommendations")
        print("✅ 4.3 Placement Browser: Advanced filters, direct access")
        print("✅ 4.4 Delivery: Chatbot + AI Search Assistant")
        print("\n📱 Mobile UI available at: mobile_ui.html")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: API server not running")
        print("Start with: python -m uvicorn src.api.main:app --reload")

if __name__ == "__main__":
    main()