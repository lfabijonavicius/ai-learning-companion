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
            with open(self.filename,'r') as file:   #Open    
                data = json.load(file)              #Read JSON
                for q_dict in data:                 #Loop through data and convert each dict to Question object
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
            