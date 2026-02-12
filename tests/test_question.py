"""Tests for Question class"""
import pytest
from question import Question


def test_create_question():
    """Test creating a basic question"""
    q = Question(
        topic="Python",
        text="What is a list?",
        question_type="mcq",
        correct_answer="A sequence",
        options=["A string", "A sequence", "A number", "A function"]
    )

    assert q.topic == "Python"
    assert q.text == "What is a list?"
    assert q.type == "mcq"
    assert q.correct_answer == "A sequence"


def test_record_attempt():
    """Test recording correct and incorrect attempts"""
    q = Question("Math", "What is 1+1?", "mcq", "2", ["1", "2", "3"])

    q.record_attempt(True)
    assert q.times_shown == 1
    assert q.times_correct == 1

    q.record_attempt(False)
    assert q.times_shown == 2
    assert q.times_correct == 1


def test_percentage_calculation():
    """Test correct percentage calculation"""
    q = Question("Math", "What is 2+2?", "mcq", "4", ["3", "4", "5"])

    # No attempts yet
    assert q.get_correct_percentage() == 0.0

    # 1 correct out of 2
    q.record_attempt(True)
    q.record_attempt(False)
    assert q.get_correct_percentage() == 50.0


def test_to_dict():
    """Test converting question to dictionary"""
    q = Question("History", "Who was Napoleon?", "freeform", "French emperor")
    data = q.to_dict()

    assert data["topic"] == "History"
    assert data["text"] == "Who was Napoleon?"
    assert data["type"] == "freeform"
    assert data["enabled"] is True
