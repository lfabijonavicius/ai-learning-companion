import streamlit as st
from quiz_manager import QuizManager
from llm_client import LLMClient
from datetime import datetime


def init_session_state():
    """Initialize session state for persistent objects and quiz state."""
    if "quiz_manager" not in st.session_state:
        st.session_state.quiz_manager = QuizManager()
    if "llm_client" not in st.session_state:
        try:
            st.session_state.llm_client = LLMClient()
        except ValueError:
            st.session_state.llm_client = None
    # Quiz session state
    if "quiz_questions" not in st.session_state:
        st.session_state.quiz_questions = []
    if "quiz_index" not in st.session_state:
        st.session_state.quiz_index = 0
    if "quiz_score" not in st.session_state:
        st.session_state.quiz_score = 0
    if "quiz_active" not in st.session_state:
        st.session_state.quiz_active = False
    if "quiz_mode" not in st.session_state:
        st.session_state.quiz_mode = None
    if "quiz_answered" not in st.session_state:
        st.session_state.quiz_answered = False
    if "quiz_feedback" not in st.session_state:
        st.session_state.quiz_feedback = None


def generate_questions_page():
    st.header("Generate Questions")

    if not st.session_state.llm_client:
        st.error("OpenAI API key not configured. Set the OPENAI_API_KEY environment variable.")
        return

    topic = st.text_input("What topic would you like to study?")
    num_questions = st.number_input("How many questions?", min_value=1, max_value=20, value=5)

    if st.button("Generate", type="primary"):
        if not topic.strip():
            st.warning("Please enter a topic.")
            return

        with st.spinner(f"Generating {num_questions} questions about {topic}..."):
            questions = st.session_state.llm_client.generate_questions(topic, num_questions)

        if questions:
            st.session_state.quiz_manager.add_questions(questions)
            st.success(f"Generated {len(questions)} questions!")
            for q in questions:
                with st.expander(f"{q.type.upper()} - {q.text[:80]}..."):
                    st.write(f"**Answer:** {q.correct_answer}")
                    if q.options:
                        st.write("**Options:**")
                        for i, opt in enumerate(q.options, 1):
                            st.write(f"  {i}. {opt}")
        else:
            st.error("Failed to generate questions. Check your API key and try again.")


def view_statistics_page():
    st.header("Statistics")

    qm = st.session_state.quiz_manager

    if not qm.questions:
        st.info("No questions available yet. Generate some questions first!")
        return

    # Overview metrics
    total = len(qm.questions)
    enabled = sum(1 for q in qm.questions if q.enabled)
    attempted = sum(1 for q in qm.questions if q.times_shown > 0)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Questions", total)
    col2.metric("Enabled", enabled)
    col3.metric("Attempted", attempted)

    st.divider()

    # Group by topic
    topics = {}
    for q in qm.questions:
        topics.setdefault(q.topic, []).append(q)

    for topic, questions in sorted(topics.items()):
        enabled_count = sum(1 for q in questions if q.enabled)
        shown = [q for q in questions if q.times_shown > 0]

        with st.expander(f"{topic} ({len(questions)} questions, {enabled_count} enabled)"):
            if shown:
                avg_success = sum(q.get_correct_percentage() for q in shown) / len(shown)
                st.progress(avg_success / 100, text=f"Average success rate: {avg_success:.1f}%")
                st.write(f"Questions attempted: {len(shown)}/{len(questions)}")
            else:
                st.write("No questions attempted yet.")

    # Token usage
    if st.session_state.llm_client:
        st.divider()
        st.subheader("API Token Usage (this session)")
        usage = st.session_state.llm_client.get_token_usage()
        c1, c2, c3 = st.columns(3)
        c1.metric("Prompt Tokens", usage["prompt_tokens"])
        c2.metric("Completion Tokens", usage["completion_tokens"])
        c3.metric("Total Tokens", usage["total_tokens"])


def _start_quiz(mode):
    """Start a quiz session."""
    qm = st.session_state.quiz_manager
    count = st.session_state.quiz_num_questions

    if mode == "practice":
        questions = []
        for _ in range(count):
            q = qm.selecting_weighted_question()
            if q:
                questions.append(q)
    else:
        questions = qm.select_unique_random_questions(count)

    st.session_state.quiz_questions = questions
    st.session_state.quiz_index = 0
    st.session_state.quiz_score = 0
    st.session_state.quiz_active = True
    st.session_state.quiz_mode = mode
    st.session_state.quiz_answered = False
    st.session_state.quiz_feedback = None


def _submit_answer(question, user_answer):
    """Evaluate the user's answer and store feedback."""
    llm = st.session_state.llm_client
    is_correct = llm.evaluate_answer(question, user_answer)
    question.record_attempt(is_correct)
    st.session_state.quiz_manager.save_questions()

    if is_correct:
        st.session_state.quiz_score += 1
        st.session_state.quiz_feedback = ("correct", "")
    else:
        st.session_state.quiz_feedback = ("incorrect", question.correct_answer)

    st.session_state.quiz_answered = True


def _next_question():
    """Move to the next question."""
    st.session_state.quiz_index += 1
    st.session_state.quiz_answered = False
    st.session_state.quiz_feedback = None


def _end_quiz():
    """End the quiz and reset state."""
    st.session_state.quiz_active = False
    st.session_state.quiz_answered = False
    st.session_state.quiz_feedback = None


def _quiz_page(mode):
    """Shared quiz UI for practice and test modes."""
    title = "Practice Mode" if mode == "practice" else "Test Mode"
    subtitle = "Focuses on difficult questions" if mode == "practice" else "Random questions, no repetition"

    st.header(title)
    st.caption(subtitle)

    qm = st.session_state.quiz_manager

    if not st.session_state.llm_client:
        st.error("OpenAI API key not configured. Set the OPENAI_API_KEY environment variable.")
        return

    if not qm.questions:
        st.info("No questions available. Generate some questions first!")
        return

    enabled_count = sum(1 for q in qm.questions if q.enabled)
    if enabled_count == 0:
        st.warning("No enabled questions available. Enable some questions in Manage Questions.")
        return

    # Quiz not started yet
    if not st.session_state.quiz_active:
        max_q = enabled_count
        st.number_input(
            "How many questions?", min_value=1, max_value=max_q,
            value=min(5, max_q), key="quiz_num_questions"
        )
        st.button("Start Quiz", type="primary", on_click=_start_quiz, args=(mode,))
        return

    questions = st.session_state.quiz_questions
    idx = st.session_state.quiz_index
    total = len(questions)

    # Quiz complete
    if idx >= total:
        score = st.session_state.quiz_score
        st.subheader(f"Quiz Complete! Score: {score}/{total}")
        pct = (score / total * 100) if total > 0 else 0
        st.progress(pct / 100, text=f"{pct:.0f}%")

        if pct >= 80:
            st.success("Great job!")
        elif pct >= 50:
            st.info("Good effort! Keep practicing.")
        else:
            st.warning("Keep studying, you'll improve!")

        # Log results for test mode
        if mode == "test":
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open("results.txt", "a") as f:
                f.write(f"{timestamp} - Score: {score}/{total}\n")
            st.caption("Results saved to results.txt")

        st.button("Start New Quiz", on_click=_end_quiz)
        return

    # Display current question
    question = questions[idx]
    st.progress((idx) / total, text=f"Question {idx + 1} of {total}")
    st.subheader(question.text)

    if question.type == "mcq" and question.options:
        options = {f"{i+1}. {opt}": str(i+1) for i, opt in enumerate(question.options)}
        selected = st.radio("Select your answer:", list(options.keys()), key=f"mcq_{idx}", label_visibility="collapsed")
        user_answer = options[selected]
    else:
        user_answer = st.text_area("Your answer:", key=f"freeform_{idx}", height=100)

    col1, col2 = st.columns([1, 5])
    with col1:
        if not st.session_state.quiz_answered:
            if st.button("Submit", type="primary"):
                if question.type != "mcq" and not user_answer.strip():
                    st.warning("Please enter an answer.")
                else:
                    with st.spinner("Evaluating..."):
                        _submit_answer(question, user_answer)
                    st.rerun()

    # Show feedback
    if st.session_state.quiz_answered and st.session_state.quiz_feedback:
        result, correct_answer = st.session_state.quiz_feedback
        if result == "correct":
            st.success("Correct!")
        else:
            st.error(f"Incorrect. The correct answer is: {correct_answer}")

        if idx + 1 < total:
            st.button("Next Question", on_click=_next_question)
        else:
            st.button("See Results", on_click=_next_question)


def practice_mode_page():
    _quiz_page("practice")


def test_mode_page():
    _quiz_page("test")


def manage_questions_page():
    st.header("Manage Questions")

    qm = st.session_state.quiz_manager

    if not qm.questions:
        st.info("No questions available. Generate some questions first!")
        return

    # Filter options
    topics = sorted(set(q.topic for q in qm.questions))
    selected_topic = st.selectbox("Filter by topic:", ["All"] + topics)

    filtered = qm.questions if selected_topic == "All" else [q for q in qm.questions if q.topic == selected_topic]

    st.write(f"Showing {len(filtered)} questions")

    for q in filtered:
        status = "Enabled" if q.enabled else "Disabled"
        pct = q.get_correct_percentage()
        stats = f"{q.times_correct}/{q.times_shown}" if q.times_shown > 0 else "Not attempted"

        with st.expander(f"{'🟢' if q.enabled else '🔴'} [{q.type.upper()}] {q.text[:70]}..."):
            st.write(f"**Topic:** {q.topic}")
            st.write(f"**Type:** {q.type}")
            st.write(f"**Answer:** {q.correct_answer}")
            if q.options:
                st.write("**Options:**")
                for i, opt in enumerate(q.options, 1):
                    st.write(f"  {i}. {opt}")
            st.write(f"**Status:** {status}")
            st.write(f"**Stats:** {stats} ({pct:.0f}% correct)")
            st.write(f"**ID:** `{q.id}`")

            action = "Disable" if q.enabled else "Enable"
            if st.button(f"{action} this question", key=f"toggle_{q.id}"):
                q.enabled = not q.enabled
                qm.save_questions()
                st.rerun()


# Main app
def main():
    st.set_page_config(page_title="AI Learning Companion", page_icon="📚", layout="wide")
    init_session_state()

    st.sidebar.title("AI Learning Companion")

    pages = {
        "Generate Questions": generate_questions_page,
        "View Statistics": view_statistics_page,
        "Practice Mode": practice_mode_page,
        "Test Mode": test_mode_page,
        "Manage Questions": manage_questions_page,
    }

    # Reset quiz when switching pages
    selection = st.sidebar.radio("Navigation", list(pages.keys()))
    if "current_page" not in st.session_state:
        st.session_state.current_page = selection
    if st.session_state.current_page != selection:
        _end_quiz()
        st.session_state.current_page = selection

    pages[selection]()


if __name__ == "__main__":
    main()
