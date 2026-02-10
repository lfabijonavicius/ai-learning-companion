import json
import random
from typing import List, Optional
from question import Question

class QuizManager:
    """Manages questions, flow, quiz session"""
    def __init__(self, filename: str = "questions.json") -> None:
        self.filename = filename
        self.questions: List[Question] = []
        self.load_questions()
        
    def load_questions(self) -> None:
        """Loading questions from JSON"""
        try:
            with open(self.filename,'r') as file:   
                data = json.load(file)              
                for q_dict in data:                
                    question = Question.from_dict(q_dict)
                    self.questions.append(question)        
        except FileNotFoundError:
            pass 
            
    def save_questions(self) -> None:
        """Save questions to JSON file"""
        data = []
        for question in self.questions: 
            data.append(question.to_dict())
            
        with open(self.filename, 'w') as file:
            json.dump(data, file, indent=4)
    
            
    def add_questions(self, new_questions: List[Question]) -> None:
        """Add new question to the question list and save"""
        self.questions.extend(new_questions)
        self.save_questions()
     
            
    def selecting_weighted_question(self) -> Optional[Question]:
        """Prioritize difficult questions"""    
        #Filter enabled questions, return None if no questions available  
        enabled = [q for q in self.questions if q.enabled]
        if not enabled:
            return None
        
        # Weight formula: 100 - correct %
        # 20% correct = 80 weight (high priority)
        # Never shown - 100 weight (high priority)
        
        weights = [100 - q.get_correct_percentage() for q in enabled]
        #k=1 picks 1 question, [0] extracts it from the returned list
        return random.choices(enabled, weights=weights, k=1)[0]
    
    def select_question_random(self) -> Optional[Question]:
        """Test mode, generates random questions"""
        enabled = [q for q in self.questions if q.enabled]
        if not enabled:
            return None
        #Returns 1 item directly (not a list like random.choices)
        return random.choice(enabled)

    def select_unique_random_questions(self, count: int) -> List[Question]:
        """Select unique random questions for test mode (no repetition)"""
        enabled = [q for q in self.questions if q.enabled]
        if not enabled:
            return []

        #Select up to 'count' questions, or all available if fewer
        actual_count = min(count, len(enabled))
        return random.sample(enabled, actual_count)