import os
from openai import OpenAI
from typing import List, Dict
from question import Question
import json

class LLMClient:
    """OpenAI API handling question generation and evaluation"""
    def __init__(self, api_key: str | None = None) -> None:
        
        self.api_key = api_key if api_key else os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        
    def generate_questions(self, topic: str, num_questions: int = 5 ) -> List[Question]:
        """Generate study questions using OpenAI LLM"""
        
        prompt = f"""Generate {num_questions} study questions about {topic}.
    Return ONLY a JSON array with this exact format (no other text):
    [
        {{
          "text": "question text here",
          "type": "mcq",
          "correct_answer": "correct_option",
          "options": ["option1", "option2", "option3", "option4"]  
        }},
        {{
          "text": "question text here",
          "type": "freeform",
          "correct_answer": "answer here",
          "options": null
        }}
    ]
    
    Mix of MCQ and freeform questions. Make them challenging and educational."""
    
        #Calling OpenAI API 
        response = self.client.chat.completions.create(
            model="chatgpt-4o-latest", 
            messages=[
                {"role": "system", "content": "You are a helpful study assistant that provides educational questions."},
                {"role": "user", "content": prompt}
            ]
        )
        response_text = response.choices[0].message.content
        
        #Parse JSON response, converts JSON string  -> Python list 
        questions_data = json.loads(response_text)
        
        #Convert to Question object
        questions = []
        #Loop through each question dictionary
        for q_data in questions_data:
        #Create a Question object for each one
            question = Question(
                topic=topic,
                text=q_data["text"],
                question_type=q_data["type"],
                correct_answer=q_data["correct_answer"],
                options=q_data.get("options"),
                source="generated"
            )
        #Append questions to the list    
            questions.append(question)
        
        #Return a list of Questions    
        return questions
        
    def evaluate_answer(self, question: Question, user_answer: str) -> bool:
        """Evaluate if user's answer is correct using AI for freeform questions"""
        
        #For MCQ comparing strings
        if question.type == "mcq":
            return user_answer == question.correct_answer
        
        else:
            prompt = f"""Question: {question.text} 
        Correct answer: {question.correct_answer}
        User's answer: {user_answer} 
        
        Is the user's answer correct? Evaluate if correct and if it's relevant.
        Respond only with one word: "correct or "incorrect"."""
        
        response = self.client.chat.completions.create(
            model="chatgpt-4o-latest", 
            messages=[
                {"role": "system", "content": "You are a helpful study assistant that provides educational questions."},
                {"role": "user", "content": prompt}
            ]
        )
        response_text = response.choices[0].message.content
        
        #Check if AI responds with "correct"
        return "correct" in response_text.lower()