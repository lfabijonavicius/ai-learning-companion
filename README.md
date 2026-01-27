# AI Learning Companion

An AI-powered study tool that generates questions, tracks performance, and helps you learn effectively.

## Features
- Generate questions using OpenAI's GPT
- Practice mode with weighted selection
- Test mode with scoring
- Performance statistics tracking
- Question management (enable/disable)

## Setup
1. Install dependencies: `pip install openai python-dotenv pytest`
2. Add your OpenAI API key to `.env` file
3. Run: `python main.py`

## Project Structure
- `main.py` - Main menu and user interface
- `question.py` - Question class
- `quiz_manager.py` - QuizManager class
- `llm_client.py` - LLM API client
- `tests/` - Unit tests
