from typing import Dict, List, Optional
import uuid #To generate unique ID's for each question

class Question:
    """Study question with performance tracking"""
    
    def __init__(self, topic: str, text: str, question_type: str, correct_answer: str,
                 options: Optional[List[str]] = None, source: str = "manual", 
                 question_id: Optional[str] = None) -> None:
        
        
        self.enabled = True
        self.times_shown = 0
        self.times_correct = 0 
        self.topic = topic
        self.text = text
        self.type = question_type
        self.correct_answer = correct_answer
        self.options = options
        self.source = source
        self.id = question_id if question_id else str(uuid.uuid4())
        
    def get_correct_percentage(self) -> float:
        """Calculate percentage of correct answers
        Returs: float: Percentage (0-100), or 0 if never shown""" 
        
        if self.times_shown == 0: #Prevent division by 0
            return 0.0
        return (self.times_correct / self.times_shown) *100
    
    def record_attempt(self, was_correct: bool) -> None:
        """Record a question attempt.
        Args: was_correct: If the user answered correctly"""
        
        self.times_shown += 1 #Increment (question shown)
        
        if was_correct: 
            self.times_correct += 1  #Increment correct count 
        
        
            
        
            
            
           
    
    