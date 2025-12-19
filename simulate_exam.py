#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
django.setup()

from restapi.models import Exam, Question, Result, CustomUser
from django.utils import timezone

user = CustomUser.objects.get(username='user1')
exam = Exam.objects.first()

print(f"User: {user.username}")
print(f"Exam: {exam.name} (Pass score: {exam.pass_score}%)\n")

# Get all questions
questions = exam.questions.all()
print(f"Total Questions: {questions.count()}\n")

# Display questions and their correct answers
print("Questions and Correct Answers:")
answers_dict = {}
for q in questions:
    print(f"Q: {q.question_text}")
    print(f"   Options: {q.options}")
    print(f"   Correct Answer: {q.correct_answer}\n")
    # Prepare answers dict
    answers_dict[f'q{q.id}'] = q.correct_answer

print("=" * 60)
print("SIMULATING EXAM SUBMISSION WITH ALL CORRECT ANSWERS")
print("=" * 60 + "\n")

# Create result
score = 0
total_questions = questions.count()
points_per_question = 100 / total_questions if total_questions > 0 else 0

print(f"Answers submitted: {answers_dict}\n")

# Calculate score
for question in questions:
    key = f'q{question.id}'
    if key in answers_dict:
        user_answer = str(answers_dict[key]).strip()
        correct_answer = str(question.correct_answer).strip()
        
        print(f"Q{question.id}: User={user_answer}, Correct={correct_answer}", end='')
        if user_answer == correct_answer:
            score += points_per_question
            print(" ✓ CORRECT")
        else:
            print(" ✗ WRONG")

score = round(score, 2)
passed = score >= exam.pass_score

print(f"\n{'=' * 60}")
print(f"FINAL SCORE: {score}%")
print(f"PASSED: {'YES' if passed else 'NO'}")
print(f"{'=' * 60}\n")

# Create the result record
result, created = Result.objects.get_or_create(
    user=user,
    exam=exam,
    defaults={
        'score': score,
        'passed': passed
    }
)

if created:
    print(f"✅ Result saved successfully!")
    print(f"   Result ID: {result.id}")
    print(f"   Score: {result.score}%")
    print(f"   Passed: {result.passed}")
else:
    print(f"⚠️  Result already exists")
    print(f"   Previous Score: {result.score}%")
