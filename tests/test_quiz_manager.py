"""Tests for QuizManager class"""
import pytest
import os
from quiz_manager import QuizManager
from question import Question


@pytest.fixture
def temp_file(tmp_path):
    """Temporary file for testing"""
    return str(tmp_path / "test_questions.json")


def test_add_questions(temp_file):
    """Test adding questions to manager"""
    manager = QuizManager(filename=temp_file)

    q1 = Question("Math", "What is 2+2?", "mcq", "4", ["3", "4", "5"])
    q2 = Question("History", "Who was Napoleon?", "freeform", "Emperor")

    manager.add_questions([q1, q2])

    assert len(manager.questions) == 2
    assert os.path.exists(temp_file)


def test_find_question_by_id(temp_file):
    """Test finding a question by ID"""
    manager = QuizManager(filename=temp_file)

    q = Question("Science", "What is H2O?", "mcq", "Water", ["Air", "Water", "Fire"])
    manager.add_questions([q])

    found = manager.find_question_by_id(q.id)
    assert found is not None
    assert found.text == "What is H2O?"

    # Test not found
    not_found = manager.find_question_by_id("fake-id-123")
    assert not_found is None


def test_select_random_question(temp_file):
    """Test random question selection"""
    manager = QuizManager(filename=temp_file)

    q1 = Question("Math", "Question 1", "mcq", "A", ["A", "B"])
    q2 = Question("Math", "Question 2", "mcq", "B", ["A", "B"])
    manager.add_questions([q1, q2])

    selected = manager.select_question_random()
    assert selected in manager.questions
