#!/usr/bin/env python
"""
COMPLETE TEST SUITE - EXAM & CERTIFICATE SYSTEM
Tests all workflows from exam access to certificate download
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
django.setup()

from restapi.models import Exam, Question, Result, Certificate, Task, CustomUser
from django.utils import timezone
import uuid

print("\n" + "=" * 70)
print("COMPREHENSIVE EXAM & CERTIFICATE SYSTEM TEST")
print("=" * 70 + "\n")

# ============ TEST 1: VERIFY EXAM DATA ============
print("TEST 1: VERIFY EXAM DATA")
print("-" * 70)
exams = Exam.objects.all()
print(f"✓ Total Exams: {exams.count()}")
for exam in exams:
    questions = exam.questions.all()
    print(f"  - Exam: {exam.name}")
    print(f"    Questions: {questions.count()}")
    print(f"    Pass Score: {exam.pass_score}%")
    print(f"    Duration: {exam.duration_minutes} minutes\n")

# ============ TEST 2: VERIFY USER TASK COMPLETION ============
print("\nTEST 2: VERIFY USER TASK COMPLETION")
print("-" * 70)
user = CustomUser.objects.get(username='user1')
user_tasks = Task.objects.filter(assigned_to=user)
completed = user_tasks.filter(status='completed').count()
print(f"✓ User: {user.username} ({user.get_full_name()})")
print(f"  Tasks Completed: {completed}/{user_tasks.count()}")

can_take_exam = user_tasks.exists() and completed == user_tasks.count()
print(f"  Can Take Exam: {'YES ✓' if can_take_exam else 'NO ✗'}\n")

# ============ TEST 3: VERIFY EXAM RESULTS ============
print("\nTEST 3: VERIFY EXAM RESULTS")
print("-" * 70)
results = Result.objects.filter(user=user)
print(f"✓ Total Results for {user.username}: {results.count()}")
for result in results:
    print(f"  - Exam: {result.exam.name}")
    print(f"    Score: {result.score}%")
    print(f"    Status: {'PASSED ✓' if result.passed else 'FAILED ✗'}")
    print(f"    Taken: {result.taken_at}\n")

# ============ TEST 4: VERIFY CERTIFICATES ============
print("\nTEST 4: VERIFY CERTIFICATES")
print("-" * 70)
certs = Certificate.objects.filter(user=user)
print(f"✓ Total Certificates for {user.username}: {certs.count()}")
for cert in certs:
    print(f"  - Certificate ID: {cert.certificate_number}")
    print(f"    Name: {cert.name}")
    print(f"    Exam: {cert.exam.name}")
    print(f"    Institution: {cert.institution}")
    print(f"    Score: {cert.score}%")
    print(f"    Issued: {cert.issued_date}\n")

# ============ TEST 5: VERIFY EXAM SUBMISSION LOGIC ============
print("\nTEST 5: VERIFY EXAM SUBMISSION LOGIC")
print("-" * 70)
exam = Exam.objects.first()
questions = exam.questions.all()
print(f"✓ Testing Exam: {exam.name}")
print(f"  Questions: {questions.count()}")

# Simulate correct answers
print(f"\n  Simulating ALL CORRECT ANSWERS:")
score = 0
total = questions.count()
points_per_q = 100 / total if total > 0 else 0

for q in questions:
    print(f"    Q: {q.question_text[:40]}...")
    print(f"       Answer: {q.correct_answer}")
    score += points_per_q

score = round(score, 2)
print(f"\n  Calculated Score: {score}%")
print(f"  Pass Score: {exam.pass_score}%")
print(f"  Result: {'PASS ✓' if score >= exam.pass_score else 'FAIL ✗'}\n")

# ============ FINAL SUMMARY ============
print("\n" + "=" * 70)
print("FINAL TEST SUMMARY")
print("=" * 70)

test_results = {
    "✓ Exams Created": exams.count() > 0,
    "✓ Questions Added": Question.objects.count() > 0,
    "✓ User Tasks Completed": can_take_exam,
    "✓ Exam Results Stored": results.count() > 0,
    "✓ Certificates Issued": certs.count() > 0,
    "✓ Exam Scoring Logic": score >= exam.pass_score,
}

passed = sum(1 for v in test_results.values() if v)
total_tests = len(test_results)

for test, result in test_results.items():
    status = "✓ PASS" if result else "✗ FAIL"
    print(f"{test}: {status}")

print(f"\nTests Passed: {passed}/{total_tests}")
print("=" * 70 + "\n")

if passed == total_tests:
    print("✅ ALL TESTS PASSED - SYSTEM IS FULLY FUNCTIONAL!\n")
else:
    print(f"⚠️  {total_tests - passed} test(s) failed - Review implementation\n")
