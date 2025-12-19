#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
django.setup()

from restapi.models import Exam, Question, Result, Task, CustomUser

print("=== EXAM & RESULT DATA CHECK ===\n")

# Check Exams
exams = Exam.objects.all()
print(f"Total Exams: {exams.count()}")
for exam in exams:
    questions = exam.questions.all()
    print(f"  - {exam.name} ({questions.count()} questions, pass score: {exam.pass_score}%)")

print(f"\nTotal Questions: {Question.objects.count()}")
print(f"Total Results: {Result.objects.count()}")

# Check Results
results = Result.objects.all().select_related('user', 'exam')
if results:
    print("\nResults:")
    for result in results:
        print(f"  - {result.user.username}: {result.exam.name} - Score: {result.score}%, Passed: {result.passed}")
else:
    print("\nNo results yet")

# Check Tasks
print(f"\nTotal Tasks: {Task.objects.count()}")
users_completed = CustomUser.objects.all()
for user in users_completed:
    user_tasks = Task.objects.filter(assigned_to=user)
    completed = user_tasks.filter(status='completed').count()
    print(f"  {user.username}: {completed}/{user_tasks.count()} tasks completed")
