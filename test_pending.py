#!/usr/bin/env python
"""Test the pending results query by creating another user and exam result"""


def main() -> None:
    import os
    import django

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
    django.setup()

    from restapi.models import Result, Certificate, Exam, CustomUser

    # Create a new test result without a certificate
    user = CustomUser.objects.get(username='user1')
    exam = Exam.objects.first()

    # Delete any existing result to test fresh
    Result.objects.filter(user=user, exam=exam).delete()

    # Create a new result
    result = Result.objects.create(
        user=user,
        exam=exam,
        score=75.0,
        passed=True
    )

    print("Created test result:")
    print(f"  User: {result.user.username}")
    print(f"  Exam: {result.exam.name}")
    print(f"  Score: {result.score}%")
    print(f"  Passed: {result.passed}\n")

    # Test pending results query
    print("Testing pending results query:")
    passed_results = Result.objects.filter(passed=True).select_related('user', 'exam')
    print(f"  Total passed results: {passed_results.count()}")

    pending = []
    for r in passed_results:
        has_cert = Certificate.objects.filter(user=r.user, exam=r.exam).exists()
        print(f"    - {r.user.username} for {r.exam.name}: Has cert? {has_cert}")
        if not has_cert:
            pending.append(r)

    print(f"\n  Pending (no certificate): {len(pending)}")
    for p in pending:
        print(f"    - {p.user.username}: Result ID {p.id}")

    if len(pending) > 0:
        print("\nSUCCESS: Pending results query works correctly!")
    else:
        print("\nERROR: No pending results found!")


if __name__ == '__main__':
    main()
