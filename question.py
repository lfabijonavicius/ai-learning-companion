from typing import Dict, List, Optional
import uuid # Generates unique ID for each question

#Blueprint for creating question objects
class Question:
    """Study question with performance tracking"""
    def __init__(self, topic: str, text: str, question_type: str, correct_answer: str,
                 options: Optional[List[str]] = None, source: str = "manual", 
                 question_id: Optional[str] = None) -> None:
        
        self.enabled = True 
        self.times_shown = 0
        self.times_correct = 0 
        self.topic = topic  #Store question data 
        self.text = text
        self.type = question_type
        self.correct_answer = correct_answer
        self.options = options
        self.source = source
        #If no ID is provided, generate unique one
        self.id = question_id if question_id else str(uuid.uuid4())
        
    def get_correct_percentage(self) -> float:
        """Calculate percentage of correct answers
        Returns: float: Percentage (0-100), or 0 if never shown""" 
        
        if self.times_shown == 0:  #Prevent division by 0
            return 0.0
        return (self.times_correct / self.times_shown) *100
    
    def record_attempt(self, was_correct: bool) -> None:
        """Update statistics after a question attempt."""
        self.times_shown += 1 
        if was_correct: 
            self.times_correct += 1 
     
    def to_dict(self) -> Dict:
        """Converting to questions.json .
        Returns dictionary containing all question data."""    
        return {"id": self.id,
                "topic": self.topic,
                "text": self.text,
                "type": self.type,
                "correct_answer": self.correct_answer,
                "options": self.options,
                "source": self.source,
                "enabled": self.enabled,
                "times_shown": self.times_shown,
                "times_correct": self.times_correct
                }
             
    @classmethod
    def from_dict(cls, data: Dict) -> 'Question':
        """Create a question using data from dictionary
        Load questions from JSON file"""
    
    #cls() is used to call the constructor with data from dictionary
    #Converts dictionary to question object
        question = cls(
           topic = data["topic"],
           text = data["text"],
           question_type = data["type"],
           correct_answer = data["correct_answer"],
           options = data.get("options", []),
           source= data.get("source", "manual"),
           question_id =data.get("id")
       )
       
    #Statistics from saved data 
        question.enabled = data.get("enabled", True)
        question.times_shown = data.get("times_shown", 0)
        question.times_correct = data.get("times_correct", 0)
    
        return question       
    
    
    