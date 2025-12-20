import json
import uuid
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

@dataclass
class Question:
    id: str
    question: str
    options: List[str]
    correct_answer: int
    subject: str
    difficulty: str
    explanation: str

@dataclass
class TestResult:
    test_id: str
    student_id: str
    score: float
    total_questions: int
    correct_answers: int
    time_taken: int
    subject_scores: Dict[str, Dict]
    timestamp: datetime

class MockTestEngine:
    def __init__(self, vector_store_manager):
        self.vector_store = vector_store_manager
        self.active_tests = {}
        self.test_results = {}
    
    def extract_questions_from_content(self, content: str, subject: str, difficulty: str) -> List[Question]:
        """Extract questions from mock test documents"""
        questions = []
        lines = content.split('\n')
        
        current_question = None
        options = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Question pattern
            if line.startswith(('Q.', 'Question', str(len(questions) + 1))):
                if current_question:
                    questions.append(Question(
                        id=str(uuid.uuid4()),
                        question=current_question,
                        options=options,
                        correct_answer=0,  # Default, should be parsed
                        subject=subject,
                        difficulty=difficulty,
                        explanation=""
                    ))
                current_question = line
                options = []
            
            # Options pattern
            elif line.startswith(('A)', 'B)', 'C)', 'D)', 'a)', 'b)', 'c)', 'd)')):
                options.append(line[2:].strip())
        
        return questions
    
    def generate_test(self, subject: Optional[str] = None, difficulty: Optional[str] = None, 
                     num_questions: int = 10) -> Dict:
        """Generate a mock test from available questions"""
        filters = {"document_type": "mock_test"}
        if subject:
            filters["subject"] = subject
        if difficulty:
            filters["difficulty"] = difficulty
        
        # Get mock test documents
        docs = self.vector_store.similarity_search_with_filters(
            "practice questions", k=20, filters=filters
        )
        
        all_questions = []
        for doc in docs:
            questions = self.extract_questions_from_content(
                doc.page_content, 
                doc.metadata.get("subject", "General"),
                doc.metadata.get("difficulty", "medium")
            )
            all_questions.extend(questions)
        
        # Select random questions
        import random
        selected_questions = random.sample(all_questions, min(num_questions, len(all_questions)))
        
        test_id = str(uuid.uuid4())
        test_data = {
            "test_id": test_id,
            "questions": [asdict(q) for q in selected_questions],
            "created_at": datetime.now().isoformat(),
            "time_limit": num_questions * 2  # 2 minutes per question
        }
        
        self.active_tests[test_id] = test_data
        return test_data
    
    def submit_test(self, test_id: str, student_id: str, answers: List[int], 
                   time_taken: int) -> TestResult:
        """Grade test and return results"""
        if test_id not in self.active_tests:
            raise ValueError("Test not found")
        
        test_data = self.active_tests[test_id]
        questions = test_data["questions"]
        
        correct_count = 0
        subject_performance = {}
        
        for i, (question, answer) in enumerate(zip(questions, answers)):
            subject = question["subject"]
            if subject not in subject_performance:
                subject_performance[subject] = {"correct": 0, "total": 0}
            
            subject_performance[subject]["total"] += 1
            
            if answer == question["correct_answer"]:
                correct_count += 1
                subject_performance[subject]["correct"] += 1
        
        # Calculate subject-wise scores
        subject_scores = {}
        for subject, perf in subject_performance.items():
            subject_scores[subject] = {
                "score": (perf["correct"] / perf["total"]) * 100,
                "correct": perf["correct"],
                "total": perf["total"]
            }
        
        result = TestResult(
            test_id=test_id,
            student_id=student_id,
            score=(correct_count / len(questions)) * 100,
            total_questions=len(questions),
            correct_answers=correct_count,
            time_taken=time_taken,
            subject_scores=subject_scores,
            timestamp=datetime.now()
        )
        
        self.test_results[f"{student_id}_{test_id}"] = result
        return result
    
    def get_student_performance(self, student_id: str) -> Dict:
        """Get student's overall performance analytics with recommendations"""
        student_tests = [r for r in self.test_results.values() if r.student_id == student_id]
        
        if not student_tests:
            return {"message": "No test history found"}
        
        avg_score = sum(t.score for t in student_tests) / len(student_tests)
        total_tests = len(student_tests)
        
        # Subject-wise performance
        subject_performance = {}
        weak_subjects = []
        
        for test in student_tests:
            for subject, scores in test.subject_scores.items():
                if subject not in subject_performance:
                    subject_performance[subject] = {"scores": [], "total_questions": 0}
                subject_performance[subject]["scores"].append(scores["score"])
                subject_performance[subject]["total_questions"] += scores["total"]
        
        # Generate recommendations
        recommendations = []
        for subject in subject_performance:
            scores = subject_performance[subject]["scores"]
            avg = sum(scores) / len(scores)
            subject_performance[subject]["average"] = avg
            
            if avg < 60:
                weak_subjects.append(subject)
                recommendations.append(f"Focus on {subject} - current average: {avg:.1f}%")
        
        if avg_score > 80:
            recommendations.append("Great performance! Try harder difficulty levels")
        elif avg_score < 50:
            recommendations.append("Review fundamentals and take more practice tests")
        
        return {
            "student_id": student_id,
            "total_tests": total_tests,
            "average_score": round(avg_score, 2),
            "subject_performance": subject_performance,
            "weak_subjects": weak_subjects,
            "recommendations": recommendations,
            "recent_tests": [asdict(t) for t in sorted(student_tests, key=lambda x: x.timestamp, reverse=True)[:5]]
        }