# AI Learning Companion

An AI-powered study tool that generates questions, tracks performance, and helps you learn effectively.

## Features
- Generate questions using OpenAI's LLM (multiple-choice and freeform)
- AI-powered semantic evaluation for freeform answers (grades based on meaning, not exact wording)
- Practice mode with weighted selection (focuses on difficult questions)
- Test mode with random question selection and scoring
- Performance statistics tracking
- Question management (enable/disable)

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Create a `.env` file in the project root (the folder containing `main.py`):
   - **Terminal:** Run `echo "OPENAI_API_KEY=your-api-key-here" > .env`
   - **VSCode:** Right-click the project folder → "New File" → name it `.env` → add:
     ```
     OPENAI_API_KEY=your-api-key-here
     ```
   - Note: Files starting with `.` are hidden by default on macOS/Linux
3. Run: `python main.py`

## Project Structure
- `main.py` - Main menu and user interface
- `question.py` - Question class
- `quiz_manager.py` - QuizManager class
- `llm_client.py` - LLM API client
- `tests/` - Unit tests
