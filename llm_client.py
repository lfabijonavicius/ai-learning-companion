import os
from openai import OpenAI, APIError, APIConnectionError, RateLimitError, AuthenticationError
from typing import List, Dict
from question import Question
import json

# OpenAI API Configuration Constants
DEFAULT_MODEL = "chatgpt-4o-latest"
QUESTION_GENERATION_TEMPERATURE = 0.8  # Higher creativity for diverse questions
ANSWER_EVALUATION_TEMPERATURE = 0.2    # Lower for consistent, strict grading

class LLMClient:
    """OpenAI API handling question generation and evaluation"""
    def __init__(self, api_key: str | None = None) -> None:

        self.api_key = api_key if api_key else os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        self.client = OpenAI(api_key=self.api_key)

        #Token usage tracking
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_tokens = 0
        
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

        try:
            #Calling OpenAI API
            response = self.client.chat.completions.create(
                model=DEFAULT_MODEL,
                temperature=QUESTION_GENERATION_TEMPERATURE,
                messages=[
                    {"role": "system", "content": "You are a helpful study assistant that provides educational questions."},
                    {"role": "user", "content": prompt}
                ]
            )

            #Track token usage
            if response.usage:
                self.total_prompt_tokens += response.usage.prompt_tokens
                self.total_completion_tokens += response.usage.completion_tokens
                self.total_tokens += response.usage.total_tokens

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

        except json.JSONDecodeError as e:
            #For JSON parsing issues
            print(f"Error parsing LLM response: {e}")
            return []
        except AuthenticationError as e:
            print(f"Authentication error: Invalid API key - {e}")
            return []
        except RateLimitError as e:
            print(f"Rate limit exceeded: {e}")
            return []
        except APIConnectionError as e:
            print(f"Connection error: Unable to reach OpenAI API - {e}")
            return []
        except APIError as e:
            print(f"OpenAI API error: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error generating questions: {e}")
            return []
        
    def evaluate_answer(self, question: Question, user_answer: str) -> bool:
        """Evaluate if user's answer is correct using AI for freeform questions"""

        #For MCQ comparing strings or numbers
        if question.type == "mcq":
            #Check if user entered a number (1, 2, 3, 4)
            if user_answer.isdigit():
                option_index = int(user_answer) - 1  #Convert to 0-based index
                if 0 <= option_index < len(question.options):
                    user_answer = question.options[option_index]
            return user_answer == question.correct_answer
        
        else:
            prompt = f"""You are a strict quiz grader.

Question: {question.text}
Correct answer: {question.correct_answer}
User's answer: {user_answer}

Must follow these rules for grading!
1. If user says "I don't know", "not sure", "no idea", -> Return "incorrect"
2. If the answer is blank or just whitespace -> Return "incorrect"
3. If the answer is completely unrelated to the question -> Return "incorrect"
4. If the answer is missing key facts from the correct answer -> Return "incorrect"
5. Only return "correct" if the answer demonstrates actual knowledge of the topic

You must respond with EXACTLY one word: "correct" or "incorrect"
No explanations, no extra text."""

            try:
                response = self.client.chat.completions.create(
                    model=DEFAULT_MODEL,
                    temperature=ANSWER_EVALUATION_TEMPERATURE,
                    messages=[
                        {"role": "system", "content": "You are a strict quiz grader. Always follow numerated grading rules exactly as specified."},
                        {"role": "user", "content": prompt}
                    ]
                )

                #Track token usage
                if response.usage:
                    self.total_prompt_tokens += response.usage.prompt_tokens
                    self.total_completion_tokens += response.usage.completion_tokens
                    self.total_tokens += response.usage.total_tokens

                response_text = response.choices[0].message.content.strip().lower()

                #Check if AI responds with exactly "correct"
                return response_text == "correct"

            except AuthenticationError as e:
                print(f"Authentication error: Invalid API key - {e}")
                return False
            except RateLimitError as e:
                print(f"Rate limit exceeded: {e}")
                return False
            except APIConnectionError as e:
                print(f"Connection error: Unable to reach OpenAI API - {e}")
                return False
            except APIError as e:
                print(f"OpenAI API error: {e}")
                return False
            except Exception as e:
                print(f"Unexpected error evaluating answer: {e}")
                return False

    def get_token_usage(self) -> Dict[str, int]:
        """Get total token usage statistics"""
        return {
            "prompt_tokens": self.total_prompt_tokens,
            "completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_tokens
        }