from typing import Dict, List, Optional
from datetime import datetime

class MockTestEngine:
    def __init__(self, vector_store_manager):
        self.vector_store = vector_store_manager
    
    def generate_test(self, subject: Optional[str] = None, difficulty: Optional[str] = None, 
                     num_questions: int = 10) -> Dict:
        return {"test_id": "test123", "questions": []}
    
    def submit_test(self, test_id: str, student_id: str, answers: List[int], 
                   time_taken: int) -> Dict:
        return {
            "test_id": test_id,
            "student_id": student_id,
            "score": 85.0,
            "total_questions": 10,
            "correct_answers": 8,
            "time_taken": time_taken,
            "subject_scores": {},
            "timestamp": datetime.now()
        }
    
    def get_student_performance(self, student_id: str) -> Dict:
        return {"student_id": student_id, "total_tests": 0, "average_score": 0}