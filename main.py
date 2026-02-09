from quiz_manager import QuizManager
from llm_client import LLMClient
from question import Question

def generate_questions_mode(quiz_manager: QuizManager, llm_client: LLMClient) -> None:
    """Generate new questions using LLM"""
    print("\n=== Generate Questions ===")

    topic = input("\nWhat topic would you like to study? ").strip()

    try:
        num_questions = int(input("How many questions? (default 5): ").strip() or "5")
    except ValueError:
        print("Invalid number. Using 5 questions")
        num_questions = 5

    print(f"\nGenerating {num_questions} questions about {topic}...")
    questions = llm_client.generate_questions(topic, num_questions)
    quiz_manager.add_questions(questions)
    print(f"Generated {len(questions)} questions!")

def view_statistics(quiz_manager: QuizManager) -> None:
    """Display statistics about questions"""
    print("\n=== Question Statistics ===")

    if not quiz_manager.questions:
        print("No questions available!")
        return

    print(f"\nTotal questions: {len(quiz_manager.questions)}")

    #Group by topic
    topics = {}
    for q in quiz_manager.questions:
        if q.topic not in topics:
            topics[q.topic] = []
        topics[q.topic].append(q)

    print(f"Topics: {len(topics)}")

    for topic, questions in topics.items():
        enabled_count = sum(1 for q in questions if q.enabled)
        print(f"\n  {topic}: {len(questions)} questions ({enabled_count} enabled)")

        #Calculate average success rate
        shown_questions = [q for q in questions if q.times_shown > 0]
        if shown_questions:
            avg_success = sum(q.get_correct_percentage() for q in shown_questions) / len(shown_questions)
            print(f"    Average success rate: {avg_success:.1f}%")
            print(f"    Questions attempted: {len(shown_questions)}/{len(questions)}")

def run_quiz(quiz_manager: QuizManager, llm_client: LLMClient, mode: str) -> None:
    """Run a quiz session (shared by practice and test modes)"""

    if not quiz_manager.questions:
        print("\nNo questions available! Please generate questions first.")
        return

    try:
        num_questions = int(input("\nHow many questions? (default 5): ").strip() or "5")
    except ValueError:
        print("Invalid number. Using 5 questions")
        num_questions = 5

    print("\nLet's start the quiz!\n")
    score = 0

    for i in range(num_questions):
        #Select question based on mode
        if mode == "practice":
            question = quiz_manager.selecting_weighted_question()
        else:
            question = quiz_manager.select_question_random()

        if not question:
            print("No more questions available!")
            break

        #Display question
        print(f"\nQuestion {i+1}/{num_questions}:")
        print(question.text)

        #Display options for MCQ
        if question.type == "mcq":
            for idx, option in enumerate(question.options, 1):
                print(f" {idx}. {option}")

        #Get user answer
        user_answer = input("Your answer: ").strip()

        #Evaluate answer
        is_correct = llm_client.evaluate_answer(question, user_answer)

        #Record attempt
        question.record_attempt(is_correct)
        quiz_manager.save_questions()

        #Show feedback
        if is_correct:
            print("Correct!")
            score += 1
        else:
            print(f"Incorrect. Correct answer is: {question.correct_answer}")

    #Final results
    print(f"\n{'='*50}")
    print(f"Quiz complete! You scored {score}/{num_questions}")
    print(f"{'='*50}")

def practice_mode(quiz_manager: QuizManager, llm_client: LLMClient) -> None:
    """Practice mode with weighted question selection"""
    print("\n=== Practice Mode ===")
    print("(Focuses on difficult questions)")
    run_quiz(quiz_manager, llm_client, "practice")

def test_mode(quiz_manager: QuizManager, llm_client: LLMClient) -> None:
    """Test mode with random question selection"""
    print("\n=== Test Mode ===")
    print("(Random questions)")
    run_quiz(quiz_manager, llm_client, "test")

def manage_questions(quiz_manager: QuizManager) -> None:
    """Manage questions (enable/disable/list)"""
    print("\n=== Manage Questions ===")

    if not quiz_manager.questions:
        print("No questions available!")
        return

    while True:
        print("\n1. List all questions")
        print("2. Enable/Disable question")
        print("3. Back to main menu")

        choice = input("\nEnter choice: ").strip()

        if choice == "1":
            #List all questions
            for i, q in enumerate(quiz_manager.questions, 1):
                status = "✓" if q.enabled else "✗"
                print(f"\n{i}. [{status}] {q.text[:60]}...")
                print(f"   Topic: {q.topic} | Type: {q.type}")
                print(f"   Stats: {q.times_shown} shown, {q.times_correct} correct")

        elif choice == "2":
            #Enable/Disable
            try:
                q_num = int(input("Enter question number: ").strip())
                if 1 <= q_num <= len(quiz_manager.questions):
                    question = quiz_manager.questions[q_num - 1]
                    question.enabled = not question.enabled
                    quiz_manager.save_questions()
                    status = "enabled" if question.enabled else "disabled"
                    print(f"Question {q_num} {status}!")
                else:
                    print("Invalid question number!")
            except ValueError:
                print("Invalid input!")

        elif choice == "3":
            break
        else:
            print("Invalid choice!")

def main():
    print("=== AI Learning Companion ===")

    quiz_manager = QuizManager()
    llm_client = LLMClient()

    print("Welcome to your personal study quiz!")

    while True:
        print("\n" + "="*50)
        print("                     MAIN MENU")
        print("="*50)
        print("1. Generate Questions")
        print("2. View Statistics")
        print("3. Practice Mode (focus on difficult questions)")
        print("4. Test Mode (random questions)")
        print("5. Manage Questions (Enable/Disable/List)")
        print("6. Exit")

        choice = input("\nEnter your choice (1-6): ").strip()

        if choice == "1":
            generate_questions_mode(quiz_manager, llm_client)
        elif choice == "2":
            view_statistics(quiz_manager)
        elif choice == "3":
            practice_mode(quiz_manager, llm_client)
        elif choice == "4":
            test_mode(quiz_manager, llm_client)
        elif choice == "5":
            manage_questions(quiz_manager)
        elif choice == "6":
            print("\nThank you for using AI Learning Companion!")
            break
        else:
            print("\nInvalid choice! Please enter 1-6.")

if __name__ == "__main__":
    main()
