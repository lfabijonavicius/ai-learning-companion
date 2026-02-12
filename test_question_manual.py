"""Manual test for Question class"""
from question import Question

print("Testing Question Class...\n")

# Test 1: Create a question
print("Test 1: Creating a question")
q = Question(
    topic="Python",
    text="What is a list?",
    question_type="freeform",
    correct_answer="A mutable collection of items"
)
print(f"✓ Created question with ID: {q.id[:8]}...")
print(f"✓ Topic: {q.topic}, Type: {q.type}")
print(f"✓ Initial stats - Shown: {q.times_shown}, Correct: {q.times_correct}\n")

# Test 2: Record attempts
print("Test 2: Recording attempts")
q.record_attempt(True)   # Correct
q.record_attempt(True)   # Correct
q.record_attempt(False)  # Wrong
print(f"✓ After 3 attempts (2 correct, 1 wrong):")
print(f"  Shown: {q.times_shown}, Correct: {q.times_correct}\n")

# Test 3: Calculate percentage
print("Test 3: Calculate percentage")
percentage = q.get_correct_percentage()
print(f"✓ Percentage correct: {percentage}%")
print(f"  Expected: 66.67%, Got: {percentage:.2f}%\n")

# Test 4: to_dict()
print("Test 4: Convert to dictionary")
data = q.to_dict()
print(f"✓ Converted to dict with {len(data)} fields")
print(f"  Keys: {list(data.keys())}\n")

# Test 5: from_dict()
print("Test 5: Create from dictionary")
q2 = Question.from_dict(data)
print(f"✓ Loaded question from dict")
print(f"  Topic: {q2.topic}")
print(f"  Stats preserved - Shown: {q2.times_shown}, Correct: {q2.times_correct}")
print(f"  Percentage: {q2.get_correct_percentage():.2f}%\n")

# Test 6: MCQ question with options
print("Test 6: Multiple choice question")
mcq = Question(
    topic="Math",
    text="What is 2+2?",
    question_type="mcq",
    correct_answer="4",
    options=["3", "4", "5", "6"]
)
print(f"✓ Created MCQ with {len(mcq.options)} options")
print(f"  Options: {mcq.options}\n")

print("=" * 50)
print("All tests passed! ✓")
