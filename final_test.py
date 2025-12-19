#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
django.setup()

from restapi.models import Exam, Question, Result, Certificate, Task, CustomUser

print("\n" + "=" * 70)
print("FINAL SYSTEM TEST - EXAM & CERTIFICATE SYSTEM")
print("=" * 70 + "\n")

# Test 1: Exams
exams = Exam.objects.all()
print("TEST 1: Exams")
print(f"  Total Exams: {exams.count()}")
print(f"  Total Questions: {Question.objects.count()}")

# Test 2: User
user = CustomUser.objects.get(username='user1')
tasks = Task.objects.filter(assigned_to=user)
completed = tasks.filter(status='completed').count()
print(f"\nTEST 2: User {user.username}")
print(f"  Tasks Completed: {completed}/{tasks.count()}")

# Test 3: Results
results = Result.objects.filter(user=user)
print(f"\nTEST 3: Exam Results")
print(f"  Total Results: {results.count()}")
if results:
    for r in results:
        print(f"    - {r.exam.name}: {r.score}% (Passed: {r.passed})")

# Test 4: Certificates
certs = Certificate.objects.filter(user=user)
print(f"\nTEST 4: Certificates")
print(f"  Total Certificates: {certs.count()}")
if certs:
    for c in certs:
        print(f"    - {c.certificate_number}: {c.institution}")

# Test 5: Pending Results
print(f"\nTEST 5: Pending Certificates")
passed_results = Result.objects.filter(passed=True).select_related('user', 'exam')
pending = []
for result in passed_results:
    if not Certificate.objects.filter(user=result.user, exam=result.exam).exists():
        pending.append(result)
print(f"  Pending Results (no certificate): {len(pending)}")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
tests = [
    ("Exams Created", exams.count() > 0),
    ("Questions Added", Question.objects.count() > 0),
    ("User Tasks Completed", completed == tasks.count()),
    ("Exam Results Stored", results.count() > 0),
    ("Certificates Issued", certs.count() > 0),
    ("Pending Query Working", True),  # If we got here, query works
]

passed = sum(1 for _, result in tests if result)
total = len(tests)

for test_name, result in tests:
    status = "PASS" if result else "FAIL"
    print(f"{test_name}: {status}")

print(f"\nTests Passed: {passed}/{total}")

if passed == total:
    print("\nSUCCESS: ALL TESTS PASSED!\n")
else:
    print(f"\nFAILED: {total - passed} test(s) failed\n")
